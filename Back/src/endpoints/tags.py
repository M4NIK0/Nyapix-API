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

@router.get("/{tag_id}", tags=["Tags management"])
async def get_tag_endpoint(request: Request, tag_id: int):
    return None

@router.get("/search", tags=["Tags management"])
async def search_tags_endpoint(request: Request, tag_name: str = Query(...)):
    return None

@router.post("", tags=["Tags management"])
@users_type.admin_required
async def post_tags_endpoint(request: Request, tag_name: str = fastapi.Query(...)):
    return None

@router.put("/{tag_id}", tags=["Tags management"])
@users_type.admin_required
async def put_tags_endpoint(request: Request, tag_id: int, tag_name: str = fastapi.Query(...)):
    return None

@router.delete("/{tag_id}", tags=["Tags management"])
@users_type.admin_required
async def delete_tags_endpoint(request: Request, tag_id: int):
    return None
