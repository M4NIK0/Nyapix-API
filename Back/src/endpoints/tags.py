import datetime
from fastapi import Query

import fastapi
from fastapi import Request
import db_management.sources as sources_db
from db_management.connection import connect_db
from utility.logging import logger
import decorators.users_type as users_type

router = fastapi.APIRouter()

@router.get("", tags=["Tags management"])
async def get_tags_endpoint(request: Request):
    return None
