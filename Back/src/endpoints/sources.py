import datetime
from fastapi import Query

import fastapi
from fastapi import Request
import db_management.sources as sources_db
from db_management.connection import connect_db
from utility.logging import logger
import decorators.users_type as users_type

router = fastapi.APIRouter()

@router.get("", tags=["Sources management"])
async def get_sources_endpoint(request: Request):
    db = None
    try:
        db = connect_db()
        sources = sources_db.list_sources(db)
        return sources
    except Exception as e:
        logger.error("Error getting sources")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("", tags=["Sources management"])
@users_type.admin_required
async def post_sources_endpoint(request: Request, source_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        success = sources_db.add_source(db, source_name)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding source")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()
