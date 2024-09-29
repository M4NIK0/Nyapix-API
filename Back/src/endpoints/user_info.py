from fastapi import APIRouter, Depends, HTTPException
from src.login_management import get_current_user
import src.models.users as users_models
import src.db_management.users as users_db

router = APIRouter()

@router.get("/me", dependencies=[Depends(get_current_user)], response_model=users_models.User)
def read_users_me(current_user: users_models.User = Depends(get_current_user)):
    user = users_db.get_user_by_id(current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
