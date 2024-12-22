import json
import random
import string
import fastapi

from db_management.connection import connect_db
import db_management.tags as tags_db
import db_management.content as content_db
import db_management.characters as characters_db
import db_management.authors as authors_db
import db_management.video as video_db
import db_management.sources as sources_db
from utility.logging import logger
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import Response
import models.content as models
import decorators.users_type as users_type
import os
import utility.video as video_utility
import hashlib

from utility.video import convert_image_to_png

router = APIRouter()

def is_video(file_type: str) -> bool:
    return file_type in ["video/mp4", "video/ogg", "video/mkv", "video/avi"]

def is_image(file_type: str) -> bool:
    return file_type in ["image/png", "image/jpeg", "image/bmp", "image/webp"]

def is_audio(file_type: str) -> bool:
    return file_type in ["audio/mp3", "audio/ogg", "audio/wav"]

def is_file_valid(file_type: str) -> bool:
    return is_video(file_type) or is_image(file_type) or is_audio(file_type)

def compute_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

@router.post("", tags=["Content management"])
@users_type.admin_or_user_required
async def post_content_endpoint(
        request: fastapi.Request,
        content: str = fastapi.Form(...),  # Accept content as a form field
        file: UploadFile = File(...)
):
    db = None
    try:
        # Parse the content JSON
        try:
            content_data = json.loads(content)
            content_obj = models.ContentPostModel(**content_data)
            pass
        except json.JSONDecodeError as e:
            return Response(content="Invalid JSON in content field", status_code=400)

        db = connect_db()

        for tag in content_obj.tags:
            if tags_db.get_tag(db, tag) is None:
                return Response(content=f"Tag with id {tag} does not exist", status_code=400)

        for character in content_obj.characters:
            if characters_db.get_character(db, character) is None:
                return Response(content=f"Character with id {character} does not exist", status_code=400)

        for author in content_obj.authors:
            if authors_db.get_author(db, author) is None:
                return Response(content=f"Author with id {author} does not exist", status_code=400)

        if sources_db.get_source(db, content_obj.source_id) is None:
            return Response(content=f"Source with id {content_obj.source} does not exist", status_code=400)

        # Write file to disk
        random_name = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        file_path = f"/tmp/{random_name}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Determine file type
        file_type = file.content_type

        # Validate file type
        if not is_file_valid(file_type):
            # Clean up file
            os.remove(file_path)
            return Response(content="Invalid file format", status_code=400)

        if is_video(file_type):
            video_utility.split_video(file_path, f"/tmp/{random_name}.chunks")

        if is_image(file_type):
            convert_image_to_png(file_path)

        # Compute file hash
        file_hash = compute_file_hash(file_path)
        content_id = content_db.add_content(db, content_obj, file_hash, request.state.user.id)

        if content_id == -1:
            return Response(status_code=409)

        if is_video(file_type):
            # Insert video inside DB
            video_db.add_video(db, content_id, file_path)
            # Clean up file
            os.remove(file_path)
            for chunk in os.listdir(f"/tmp/{random_name}.chunks"):
                os.remove(f"/tmp/{random_name}.chunks/{chunk}")
            os.removedirs(f"/tmp/{random_name}.chunks")

        if is_image(file_type):
            # Insert image inside DB
            video_db.add_image(db, content_id, file_path + ".png")
            # Clean up file
            os.remove(file_path)
            os.remove(file_path + ".png")

        # Process further logic here
    except Exception as e:
        logger.error("Error adding content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()
