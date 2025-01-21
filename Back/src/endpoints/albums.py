import fastapi
import decorators.users_type as users_type
from utility.logging import logger
from db_management.connection import connect_db
import db_management.albums as albums_db
import models.content as models
from fastapi import Query, Response
import models.users as user_models
import os

router = fastapi.APIRouter()

@router.post("", tags=["Albums management"])
@users_type.admin_or_user_required
async def post_albums_endpoint(request: fastapi.Request, info: models.AlbumPostModel = fastapi.Body(...)):
    db = None
    try:
        db = connect_db()
        success = albums_db.add_album(db, request.state.user.id, info)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("/{album_id/add-content", tags=["Albums management"])
@users_type.admin_or_user_required
async def post_albums_add_content_endpoint(request: fastapi.Request, album_id: int, content_id: int):
    db = None
    try:
        db = connect_db()
        if not albums_db.is_user_album(db, request.state.user.id, album_id):
            return fastapi.responses.Response(status_code=403)
        success = albums_db.add_content_to_album(db, album_id, content_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding content to album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{album_id/remove-content", tags=["Albums management"])
@users_type.admin_or_user_required
async def delete_albums_remove_content_endpoint(request: fastapi.Request, album_id: int, content_id: int):
    db = None
    try:
        db = connect_db()
        if not albums_db.is_user_album(db, request.state.user.id, album_id):
            return fastapi.responses.Response(status_code=403)
        albums_db.remove_content_from_album(db, album_id, content_id)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error removing content from album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/search", tags=["Albums management"])
async def search_content_endpoint(request: fastapi.Request,
                                  needed_tags: list[int] = Query(None), needed_characters: list[int] = Query(None), needed_authors: list[int] = Query(None),
                                  tags_to_exclude: list[int] = Query(None), characters_to_exclude: list[int] = Query(None), authors_to_exclude: list[int] = Query(None),
                                  page: int = Query(1), max_results: int = Query(10)) -> models.AlbumPageModel:
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

        content = albums_db.search_album(db, needed_tags, needed_characters, needed_authors,
                                         tags_to_exclude, characters_to_exclude, authors_to_exclude, max_results, page, request.state.user.id)

        if content is None:
            return Response(status_code=500)

        return content
    except Exception as e:
        logger.error("Error searching content")
        logger.error(e)
        return Response(status_code=500)
    finally:
        if db is not None:
            db.close()


@router.put("/{album_id}", tags=["Albums management"])
@users_type.admin_or_user_required
async def put_albums_endpoint(request: fastapi.Request, album_id: int, info: models.AlbumUpdateModel = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        if not albums_db.is_user_album(db, request.state.user.id, album_id):
            return fastapi.responses.Response(status_code=403)
        success = albums_db.edit_album(db, album_id, info)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{album_id}", tags=["Albums management"])
@users_type.admin_or_user_required
async def delete_albums_endpoint(request: fastapi.Request, album_id: int):
    db = None
    try:
        db = connect_db()
        if not albums_db.is_user_album(db, request.state.user.id, album_id):
            return fastapi.responses.Response(status_code=403)
        success = albums_db.delete_album(db, album_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{album_id}", tags=["Albums management"])
async def get_album_endpoint(request: fastapi.Request, album_id: int) -> models.AlbumContentModel:
    db = None
    try:
        db = connect_db()
        album = albums_db.get_album(db, request.state.user.id, album_id)
        if album is None:
            return fastapi.responses.Response(status_code=404)
        return album
    except Exception as e:
        logger.error("Error getting album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{album_id_id}/who", tags=["Administration"])
@users_type.admin_required
async def get_album_who_endpoint(request: fastapi.Request, album_id: int) -> user_models.UserModel:
    db = None
    try:
        db = connect_db()
        album = albums_db.get_album_who(db, album_id)
        if album is None:
            return fastapi.responses.Response(status_code=404)
        return album
    except Exception as e:
        logger.error("Error getting album")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()