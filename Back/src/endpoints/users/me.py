from fastapi import APIRouter, Depends, HTTPException
from src.login_management import get_current_user, hash_password
import src.decorators as decorators
import src.models.users as users_models
import src.models.general_responses as general_responses_models
import src.models.users_history as users_history_models
import src.db_management.users.history as users_history_db
from typing import List
import re

import src.db_management.users.users as users_db


router = APIRouter()


@router.get("/content-history", dependencies=[Depends(get_current_user)], response_model=List[users_history_models.UserContentHistory])
@decorators.user_existence_required()
def read_users_me_content_history(current_user: users_models.User = Depends(get_current_user)):
    history = users_history_db.get_user_content_history(current_user.id)

    return history


@router.get("/album-history", dependencies=[Depends(get_current_user)], response_model=List[users_history_models.UserAlbumHistory])
@decorators.user_existence_required()
def read_users_me_album_history(current_user: users_models.User = Depends(get_current_user)):
    history = users_history_db.get_user_album_history(current_user.id)

    return history


@router.delete("", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_existence_required()
def delete_users_me(current_user: users_models.User = Depends(get_current_user)):
    deleted = users_db.delete_user(current_user.id)
    if deleted:
        return general_responses_models.Message(message="Account deleted successfully")

    raise HTTPException(status_code=500, detail="Could not delete user")


@router.put("", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_existence_required()
def edit_users_me(new_data: users_models.UserUpdate, current_user: users_models.User = Depends(get_current_user)):
    if new_data.username:
        if not re.match(r"^[a-z0-9_]{3,20}$", new_data.username):
            raise HTTPException(status_code=400, detail="Invalid username")

        if users_db.get_user_by_username(new_data.username):
            raise HTTPException(status_code=400, detail="Username already exists")

    edited = users_db.update_user(current_user.id, username=new_data.username, nickname=new_data.nickname, hashed_password=hash_password(new_data.password) if new_data.password else None)

    if edited:
        return general_responses_models.Message(message="User updated successfully")

    raise HTTPException(status_code=500, detail="Could not update user")


@router.get("", dependencies=[Depends(get_current_user)], response_model=users_models.User)
@decorators.user_existence_required()
def read_users_me(current_user: users_models.User = Depends(get_current_user)):
    user = users_db.get_user_by_id(current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
