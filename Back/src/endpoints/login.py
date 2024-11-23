import fastapi
import utility.token as token_utility
from db_management.connection import connect_db

router = fastapi.APIRouter()

@router.post("/login")
async def post_login_endpoint():
    try:
        db = connect_db()
        db.close()
        token = token_utility.generate_session_token(None)
        return {"token": token}
    except:
        return fastapi.responses.Response(status_code=500)

@router.delete("/logout")
async def delete_logout_endpoint():
    return {}
