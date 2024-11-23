import fastapi
import utility.token as token_utility
from db_management.users import check_user_exists
from utility.logging import logger
from db_management.connection import connect_db
import db_management.users as users_db
import models.users as users_models
import models.login as login_models
import db_management.login as login_db

router = fastapi.APIRouter()

@router.post("/register")
async def post_register_endpoint(new_user: users_models.UserRegisterModel):
    db = None
    try:
        db = connect_db()
        exists = users_db.check_user_exists(db, new_user.username)
        if exists:
            return fastapi.responses.Response(status_code=409)
        result = users_db.register(db, new_user.username, new_user.nickname, new_user.password)
        if result is None:
            return fastapi.responses.Response(status_code=409)
    except Exception as e:
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("/login")
async def post_login_endpoint(login: users_models.UserLoginModel):
    db = None
    try:
        db = connect_db()
        logged = login_db.check_user_login(db, login.username, login.password)
        if not logged:
            return fastapi.responses.Response(status_code=401)
        user = users_db.get_user(db, login.username)
        if user is None:
            return fastapi.responses.Response(status_code=401)
        token = login_db.create_session(db, user.id)
        return {"token": token}
    except Exception as e:
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/logout")
async def delete_logout_endpoint():
    return {}
