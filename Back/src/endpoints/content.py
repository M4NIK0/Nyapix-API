import json
import random
import string
import fastapi
from starlette.responses import FileResponse, StreamingResponse

from db_management.connection import connect_db
import db_management.tags as tags_db
import db_management.content as content_db
import db_management.characters as characters_db
import db_management.authors as authors_db
import db_management.stream as video_db
import db_management.sources as sources_db
from db_management.content import has_user_access, get_image_content_id, get_video_content_id, is_user_content
from models.content import ContentModel
from utility.logging import logger
from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import Response
import models.content as models
import decorators.users_type as users_type
import os
import utility.media as video_utility
import hashlib

from utility.media import convert_image_to_png

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

@router.get("/my", tags=["Content management"])
async def get_my_content_endpoint(request: fastapi.Request, page: int = Query(...), max_results: int = Query(10)) -> models.ContentPageModel:
    db = None
    try:
        db = connect_db()
        content = content_db.get_user_content(db, request.state.user.id, max_results, page)

        for item in content.contents:
            item.url = f"{request.base_url}{item.url}"

        return content
    except Exception as e:
        logger.error("Error getting user content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/search", tags=["Content management"])
async def search_content_endpoint(request: fastapi.Request,
                                  needed_tags: list[int] = Query(None), needed_characters: list[int] = Query(None), needed_authors: list[int] = Query(None),
                                  tags_to_exclude: list[int] = Query(None), characters_to_exclude: list[int] = Query(None), authors_to_exclude: list[int] = Query(None),
                                  page: int = Query(1), max_results: int = Query(10)) -> models.ContentPageModel:
    db = None
    try:
        db = connect_db()

        if needed_tags is None:
            needed_tags = []
        if needed_characters is None:
            needed_characters = []
        if needed_authors is None:
            needed_authors = []
        if tags_to_exclude is None:
            tags_to_exclude = []
        if characters_to_exclude is None:
            characters_to_exclude = []
        if authors_to_exclude is None:
            authors_to_exclude = []

        content = content_db.search_content(db, needed_tags, needed_characters, needed_authors,
                                            tags_to_exclude, characters_to_exclude, authors_to_exclude, max_results, page)

        if content is None:
            return Response(status_code=500)

        for item in content.contents:
            item.url = f"{request.base_url}{item.url}"

        return content
    except Exception as e:
        logger.error("Error searching content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{content_id}/thumb")
async def get_content_thumb_endpoint(request: fastapi.Request, content_id: int):
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, request.state.user.id, content_id):
            return Response(status_code=403)

        miniature = content_db.get_miniature(db, content_id)

        if miniature is None:
            return Response(status_code=404)

        return StreamingResponse(async_bytes_it(miniature), media_type="image/png")
    except Exception as e:
        logger.error("Error getting content thumbnail")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{content_id}", tags=["Content management"])
async def get_content_endpoint(request: fastapi.Request, content_id: int) -> ContentModel:
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, request.state.user.id, content_id):
            return Response(status_code=403)

        content = content_db.get_content(db, content_id)

        if content is None:
            return Response(status_code=404)

        content.url = f"{request.base_url}{content.url}"

        return content
    except Exception as e:
        logger.error("Error getting content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{content_id}", tags=["Content management"])
@users_type.admin_or_user_required
async def put_content_endpoint(request: fastapi.Request, content_id: int, content: models.ContentUpdateModel):
    db = None
    try:
        db = connect_db()

        if not is_user_content(db, request.state.user.id, content_id):
            return Response(status_code=403)

        if content.tags is not None:
            for tag in content.tags:
                if tags_db.get_tag(db, tag) is None:
                    return Response(content=f"Tag with id {tag} does not exist", status_code=400)

        if content.characters is not None:
            for character in content.characters:
                if characters_db.get_character(db, character) is None:
                    return Response(content=f"Character with id {character} does not exist", status_code=400)

        if content.authors is not None:
            for author in content.authors:
                if authors_db.get_author(db, author) is None:
                    return Response(content=f"Author with id {author} does not exist", status_code=400)

        if content.source_id is not None:
            if sources_db.get_source(db, content.source_id) is None:
                return Response(content=f"Source with id {content.source} does not exist", status_code=400)

        success = content_db.update_content(db, content_id, content)
        if not success:
            return Response(status_code=409)
    except Exception as e:
        logger.error("Error updating content")
        logger.error(e)
        return Response(status_code=500)

    return Response(status_code=200)

@router.delete("/{content_id}", tags=["Content management"])
@users_type.admin_or_user_required
async def delete_content_endpoint(request: fastapi.Request, content_id: int):
    db = None
    try:
        db = connect_db()

        if not is_user_content(db, request.state.user.id, content_id):
            return Response(status_code=403)

        success = content_db.delete_content(db, content_id)
        if not success:
            return Response(status_code=409)
    except Exception as e:
        logger.error("Error deleting content")
        logger.error(e)
        return Response(status_code=500)

    return Response(status_code=200)

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

        converted_path = None
        miniature_path = None

        if is_video(file_type):
            converted_path = video_utility.convert_video_to_mp4(f"/tmp/{random_name}")
            miniature_path = video_utility.generate_video_miniature(converted_path, int(video_utility.get_video_length(converted_path) / 4), 480)

        if is_image(file_type):
            converted_path = convert_image_to_png(file_path)
            miniature_path = video_utility.generate_image_miniature(converted_path, 480)

        # Compute file hash
        file_hash = compute_file_hash(file_path)
        content_id = content_db.add_content(db, content_obj, file_hash, request.state.user.id)

        if content_id == -1:
            return Response(status_code=409)

        if is_video(file_type):
            video_db.add_video(db, content_id, converted_path)
            os.remove(file_path)

        if is_image(file_type):
            video_db.add_image(db, content_id, converted_path)
            os.remove(file_path)

        content_db.add_miniature(db, content_id, miniature_path)
        os.remove(converted_path)
    except Exception as e:
        logger.error("Error adding content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

async def async_bytes_it(data: bytes):
    yield data

@router.get("/video/{video_id}", tags=["Content management"])
async def get_video_endpoint(request: fastapi.Request, video_id: int):
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, request.state.user.id, get_video_content_id(db, video_id)):
            return Response(status_code=403)

        video = video_db.get_video(db, video_id)
        if video is None:
            return Response(status_code=404)
        return StreamingResponse(async_bytes_it(video), media_type="video/mp4")
    except Exception as e:
        logger.error("Error getting video")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/image/{image_id}", tags=["Content management"])
async def get_image_endpoint(request: fastapi.Request, image_id: int):
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, request.state.user.id, get_image_content_id(db, image_id)):
            return Response(status_code=403)

        image = video_db.get_image(db, image_id)
        if image is None:
            return Response(status_code=404)
        return StreamingResponse(async_bytes_it(image), media_type="image/png")
    except Exception as e:
        logger.error("Error getting image")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

# @router.get("/video/{video_id}/manifest", tags=["Content management"])
# async def get_video_manifest_endpoint(request: fastapi.Request, video_id: int):
#     db = None
#     try:
#         db = connect_db()
#
        # Fetch video chunk data
        # manifest = video_db.get_video_manifest(db, video_id)
        # if manifest is None:
        #     return Response(status_code=404)
        #
        # return Response(content=manifest)
    # except Exception as e:
    #     logger.error("Error getting video manifest")
    #     logger.error(e)
    #     return Response(status_code=500)
    # finally:
    #     if db is not None:
    #         db.close()
#
#
# @router.get("/video/{video_id}/segments/{chunk_id}", tags=["Content management"])
# async def get_video_chunk_endpoint(request: fastapi.Request, video_id: int, chunk_id: int):
#     db = None
#     try:
#         db = connect_db()
#         chunk = video_db.get_video_chunk(db, video_id, chunk_id)
#
#         if chunk is None:
#             return Response(status_code=404)
#
#         return StreamingResponse(async_bytes_it(chunk), media_type="video/mp4")
#     except Exception as e:
#         logger.error("Error getting video chunk")
#         logger.error(e)
#         return Response(status_code=500)
#     finally:
#         if db is not None:
#             db.close()
