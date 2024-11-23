import fastapi
import utility.token as token_utility

router = fastapi.APIRouter()

@router.post("/login")
async def post_login_endpoint():
    return {token_utility.generate_session_token(None)}

@router.delete("/logout")
async def delete_logout_endpoint():
    return {}
