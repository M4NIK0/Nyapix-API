import fastapi
import utility.token as token_utility
from utility.logging import logger
from db_management.connection import connect_db
import db_management.users as users_db

router = fastapi.APIRouter()

@router.post("/register")
async def post_register_endpoint():
    db = None
    try:
        db = connect_db()
        result = users_db.register(db, "test", "test", "test")
        if result is None:
            return fastapi.responses.Response(status_code=409)
    except Exception as e:
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("/login")
async def post_login_endpoint():
    try:
        db = connect_db()
        db.close()
        token = token_utility.generate_session_token(None)
        return {"token": token}
    except Exception as e:
        logger.error(e)
        return fastapi.responses.Response(status_code=500)

@router.delete("/logout")
async def delete_logout_endpoint():
    return {}
