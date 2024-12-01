import datetime
from fastapi import Query

import fastapi
from fastapi import Request
import db_management.tags as tags_db
from db_management.connection import connect_db
from utility.logging import logger
import decorators.users_type as users_type
import models.content as content_models

router = fastapi.APIRouter()

@router.get("/search", tags=["Tags management"])
async def search_tags_endpoint(request: Request, tag_name: str = Query(...), max_results: int = Query(10)) -> content_models.TagPageModel:
    db = None
    try:
        db = connect_db()
        tag_name = tag_name.strip().lower().replace(" ", "_")
        tags = tags_db.search_tags(db, tag_name, max_results)
        return tags
    except Exception as e:
        logger.error("Error searching tags")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("", tags=["Tags management"])
async def get_tags_endpoint(request: Request, page: int = Query(1), size: int = Query(10)) -> content_models.TagPageModel:
    db = None
    try:
        db = connect_db()
        tags = tags_db.get_tags_page(db, page, size)
        return tags
    except Exception as e:
        logger.error("Error getting tags")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{tag_id}", tags=["Tags management"])
async def get_tag_endpoint(request: Request, tag_id: int) -> content_models.TagModel:
    db = None
    try:
        db = connect_db()
        tag = tags_db.get_tag(db, tag_id)
        if tag is None:
            return fastapi.responses.Response(status_code=404)
        return tag
    except Exception as e:
        logger.error("Error getting tag")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("", tags=["Tags management"])
@users_type.admin_required
async def post_tags_endpoint(request: Request, tag_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        tag_name = tag_name.strip().lower().replace(" ", "_")
        success = tags_db.add_tag(db, tag_name, request.state.user.id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding tag")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{tag_id}", tags=["Tags management"])
@users_type.admin_required
async def put_tags_endpoint(request: Request, tag_id: int, tag_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        tag_name = tag_name.strip().lower().replace(" ", "_")
        success = tags_db.edit_tag(db, tag_id, tag_name)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating tag")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{tag_id}", tags=["Tags management"])
@users_type.admin_required
async def delete_tags_endpoint(request: Request, tag_id: int):
    db = None
    try:
        db = connect_db()
        success = tags_db.delete_tag(db, tag_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting tag")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()
