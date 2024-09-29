from fastapi import APIRouter, Depends, HTTPException
from src.login_management import get_current_user
from src.logs import logger
import src.decorators as decorators
import src.models.general_responses as general_responses_models
import src.models.users as users_models
import src.db_management.content.tags as tags_db
from typing import List
import src.models.content as content_models


router = APIRouter()


@router.get("/search/{string}", dependencies=[Depends(get_current_user)], response_model=List[content_models.Tag])
@decorators.user_not_guest_required()
def search_tags_endpoint(string: str, current_user: users_models.User = Depends(get_current_user)):
    tags = tags_db.search_tags(string)
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found")

    return tags


@router.get("/name/{tag_name}", dependencies=[Depends(get_current_user)], response_model=content_models.Tag)
@decorators.user_not_guest_required()
@decorators.tag_name_existence_required()
def get_tag_by_name_endpoint(tag_name: str, current_user: users_models.User = Depends(get_current_user)):
    tag = tags_db.get_tag_by_name(tag_name)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag


@router.put("/{tag_id}", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
@decorators.tag_id_existence_required()
@decorators.tag_owner_or_admin_required()
def put_tags_endpoint(tag_id: int, tag_name: str, current_user: users_models.User = Depends(get_current_user)):
    if tags_db.get_tag_by_name(tag_name):
        raise HTTPException(status_code=400, detail="The tag name you want to set already exists")

    result = tags_db.update_tag_by_id(tag_id, tag_name)

    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while updating the tag")

    return general_responses_models.Message(message="Tag updated successfully")


@router.delete("/{tag_id}", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
@decorators.tag_id_existence_required()
@decorators.tag_owner_or_admin_required()
def delete_tags_endpoint(tag_id: int, current_user: users_models.User = Depends(get_current_user)):
    result = tags_db.delete_tag(tag_id)
    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the tag")

    return general_responses_models.Message(message="Tag deleted successfully")


@router.get("/{tag_id}", dependencies=[Depends(get_current_user)], response_model=content_models.Tag)
@decorators.user_not_guest_required()
@decorators.tag_id_existence_required()
def get_tag_by_id_endpoint(tag_id: int, current_user: users_models.User = Depends(get_current_user)):
    tag = tags_db.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag


@router.get("", dependencies=[Depends(get_current_user)], response_model=List[content_models.Tag])
@decorators.user_not_guest_required()
def get_tags_endpoint(current_user: users_models.User = Depends(get_current_user)):
    tags = tags_db.get_tags()
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found")

    return tags


@router.post("", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
def post_tags_endpoint(tag_name: str, current_user: users_models.User = Depends(get_current_user)):
    if tags_db.get_tag_by_name(tag_name):
        raise HTTPException(status_code=400, detail="The tag name you want to set already exists")

    result = tags_db.add_tag(tag_name, current_user.id)
    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while adding the tag (maybe because it already exists)")

    return general_responses_models.Message(message="Tag added successfully")
