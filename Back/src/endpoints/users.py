import fastapi

router = fastapi.APIRouter()

@router.get("/")
async def get_users():
    return {"users": []}
