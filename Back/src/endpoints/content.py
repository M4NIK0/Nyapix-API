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
from db_management.content import has_user_access, get_image_content_id, get_video_content_id, is_user_content, get_audio_content_id
from models.content import ContentModel
from models.users import UserModel
from utility.logging import logger
from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import Response
import models.content as models
import decorators.users_type as users_type
import os
import utility.media as video_utility
import hashlib
import db_management.users as users_db

from utility.media import convert_image_to_png, convert_audio_to_wav

router = APIRouter()

def is_video(file_type: str) -> bool:
    return file_type in ["video/mp4", "video/ogg", "video/mkv", "video/avi"]

def is_image(file_type: str) -> bool:
    return file_type in ["image/png", "image/jpeg", "image/bmp", "image/webp"]

def is_audio(file_type: str) -> bool:
    return file_type in ["audio/mp3", "audio/ogg", "audio/wav", "audio/mpeg"]

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
            is_https = os.getenv("IS_HTTPS")
            if is_https  == "yes":
                is_https = True
            else:
                is_https = False
            item.url = f"{request.base_url}{item.url}"
            if is_https:
                item.url = item.url.replace("http://", "https://")

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
                                            tags_to_exclude, characters_to_exclude, authors_to_exclude, max_results, page, request.state.user.id)

        if content is None:
            return Response(status_code=500)

        for item in content.contents:
            is_https = os.getenv("IS_HTTPS")
            if is_https  == "yes":
                is_https = True
            else:
                is_https = False
            item.url = f"{request.base_url}{item.url}"
            if is_https:
                item.url = item.url.replace("http://", "https://")

        return content
    except Exception as e:
        logger.error("Error searching content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{content_id}/thumb", tags=["Content management"])
async def get_content_thumb_endpoint(request: fastapi.Request, content_id: int):
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, content_id, request.state.user.id):
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

@router.get("/{content_id}/who", tags=["Administration"])
@users_type.admin_required
async def get_content_full_endpoint(request: fastapi.Request, content_id: int) -> UserModel:
    db = None
    try:
        db = connect_db()

        user_id = content_db.get_content_user_id(db, content_id)
        if user_id is None:
            return Response(status_code=404)

        user = users_db.get_user(db, user_id)
        if user is None:
            return Response(status_code=404)

        return user
    except Exception as e:
        logger.error("Error getting content owner")
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

        if not has_user_access(db, content_id, request.state.user.id):
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

        if not is_user_content(db, content_id, request.state.user.id):
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

        if not is_user_content(db, content_id, request.state.user.id):
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

        if is_audio(file_type):
            converted_path = convert_audio_to_wav(file_path)

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

        if is_audio(file_type):
            video_db.add_audio(db, content_id, converted_path)
            os.remove(file_path)

        if miniature_path is not None:
            content_db.add_miniature(db, content_id, miniature_path)
            os.remove(miniature_path)

        os.remove(converted_path)

        return Response(status_code=200)
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

        if not has_user_access(db, get_video_content_id(db, video_id), request.state.user.id):
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

        if not has_user_access(db, get_image_content_id(db, image_id), request.state.user.id):
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

@router.get("/audio/{audio_id}", tags=["Content management"])
async def get_audio_endpoint(request: fastapi.Request, audio_id: int):
    db = None
    try:
        db = connect_db()

        if not has_user_access(db, request.state.user.id, audio_id):
            return Response(status_code=403)

        audio = video_db.get_audio(db, audio_id)
        if audio is None:
            return Response(status_code=404)
        return StreamingResponse(async_bytes_it(audio), media_type="audio/wav")
    except Exception as e:
        logger.error("Error getting audio")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/video/{video_id}/content-id", tags=["Content management"])
async def get_video_content_id_endpoint(request: fastapi.Request, video_id: int):
    db = None
    try:
        db = connect_db()
        content_id = get_video_content_id(db, video_id)
        if content_id is None:
            return Response(status_code=404)
        if not has_user_access(db, content_id, request.state.user.id):
            return Response(status_code=403)
        return Response(content=str(content_id))
    except Exception as e:
        logger.error("Error getting video content id")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/image/{image_id}/content-id", tags=["Content management"])
async def get_image_content_id_endpoint(request: fastapi.Request, image_id: int):
    db = None
    try:
        db = connect_db()
        content_id = get_image_content_id(db, image_id)
        if content_id is None:
            return Response(status_code=404)
        if not has_user_access(db, content_id, request.state.user.id):
            return Response(status_code=403)
        return Response(content=str(content_id))
    except Exception as e:
        logger.error("Error getting image content id")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/audio/{audio_id}/content-id", tags=["Content management"])
async def get_audio_content_id_endpoint(request: fastapi.Request, audio_id: int):
    db = None
    try:
        db = connect_db()
        content_id = get_audio_content_id(db, audio_id)
        if content_id is None:
            return Response(status_code=404)
        if not has_user_access(db, content_id, request.state.user.id):
            return Response(status_code=403)
        return Response(content=str(audio_id))
    except Exception as e:
        logger.error("Error getting audio content id")
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
