from fastapi import APIRouter, Depends, HTTPException
from src.login_management import get_current_user
import src.models.users as users_models

router = APIRouter()

@router.get("/me", dependencies=[Depends(get_current_user)], response_model=users_models.User)
def read_users_me(current_user: users_models.User = Depends(get_current_user)):
    return current_user
