import datetime

import fastapi
from fastapi import Request
import db_management.users as users_db
from db_management.connection import connect_db
from models.users import FullUserModel, UserUpdateModel, UserPageModel
from utility.logging import logger

import decorators.users_type as users_type

router = fastapi.APIRouter()

@router.get("/me", tags=["Account management"])
async def get_me_endpoint(request: Request):
    db = None
    try:
        db = connect_db()
        user_info = users_db.get_full_user(db, request.state.user.id)
        if user_info is None:
            return fastapi.responses.Response(status_code=404)
        user_info.username = request.state.user.username
        user_info.nickname = request.state.user.nickname
        user_info.id = request.state.user.id
        user_info.type = request.state.user.type
        return user_info
    except Exception as e:
        logger.error("Error getting full user info")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/me", tags=["Account management"])
async def put_me_endpoint(user_query: UserUpdateModel, request: Request):
    db = None
    try:
        db = connect_db()
        success = users_db.update_user(db, user_query, request.state.user.id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating user")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/me", tags=["Account management"])
async def delete_me_endpoint(request: Request):
    db = None
    try:
        db = connect_db()
        success = users_db.delete_user(db, request.state.user.id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting user")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/search", tags=["Administration"])
@users_type.admin_required
async def get_search_user_endpoint(request: Request, user_query: str, max_results: int, page: int) -> UserPageModel:
    db = None
    try:
        db = connect_db()
        user_info = users_db.search_user(db, user_query, max_results, page)
        if user_info is None:
            return fastapi.responses.Response(status_code=404)
        return user_info
    except Exception as e:
        logger.error("Error getting user info")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{user_id}", tags=["Administration"])
@users_type.admin_required
async def get_user_endpoint(request: Request, user_id: int) -> FullUserModel:
    db = None
    try:
        db = connect_db()
        user_info = users_db.get_full_user(db, user_id)
        if user_info is None:
            return fastapi.responses.Response(status_code=404)
        return user_info
    except Exception as e:
        logger.error("Error getting user info")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{user_id}/account-type", tags=["Administration"])
@users_type.admin_required
async def put_user_account_type_endpoint(request: Request, user_id: int, account_type: int):
    db = None
    try:
        db = connect_db()
        success = users_db.update_user_type(db, user_id, account_type)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating user account type")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{user_id}", tags=["Administration"])
@users_type.admin_required
async def put_user_endpoint(user_id: int, request: Request, user_query: UserUpdateModel = fastapi.Body(...)):
    db = None
    try:
        db = connect_db()
        success = users_db.update_user(db, user_query, user_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating user")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{user_id}", tags=["Administration"])
@users_type.admin_required
async def delete_user_endpoint(request: Request, user_id: int):
    db = None
    try:
        db = connect_db()
        success = users_db.delete_user(db, user_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting user")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()
