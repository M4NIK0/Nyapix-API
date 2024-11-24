import datetime

import fastapi
from fastapi import Request
import db_management.users as users_db
from db_management.connection import connect_db
from models.users import FullUserModel, UserUpdateModel
from utility.logging import logger

router = fastapi.APIRouter()

@router.get("/me")
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

@router.put("/me")
async def put_me_endpoint(user: UserUpdateModel, request: Request):
    db = None
    try:
        db = connect_db()
        success = users_db.update_user(db, user, request.state.user.id)
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

@router.delete("/me")
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
