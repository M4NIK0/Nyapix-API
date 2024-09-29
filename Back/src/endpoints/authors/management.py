from fastapi import APIRouter, Depends, HTTPException
from src.login_management import get_current_user
from src.logs import logger
import src.decorators as decorators
import src.models.general_responses as general_responses_models
import src.models.users as users_models
import src.db_management.content.authors as authors_db
from typing import List
import src.models.content as content_models


router = APIRouter()


@router.get("/search/{string}", dependencies=[Depends(get_current_user)], response_model=List[content_models.Author])
@decorators.user_not_guest_required()
def search_authors_endpoint(string: str, current_user: users_models.User = Depends(get_current_user)):
    tags = authors_db.search_authors(string)
    if not tags:
        raise HTTPException(status_code=404, detail="No authors found")

    return tags


@router.get("/name/{author_name}", dependencies=[Depends(get_current_user)], response_model=content_models.Author)
@decorators.user_not_guest_required()
@decorators.author_name_existence_required()
def get_author_by_name_endpoint(author_name: str, current_user: users_models.User = Depends(get_current_user)):
    tag = authors_db.get_author_by_name(author_name)
    if not tag:
        raise HTTPException(status_code=404, detail="Author not found")

    return tag


@router.put("/{author_id}", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
@decorators.author_id_existence_required()
@decorators.author_owner_or_admin_required()
def put_authors_endpoint(author_id: int, author_name: str, current_user: users_models.User = Depends(get_current_user)):
    if authors_db.get_author_by_name(author_name):
        raise HTTPException(status_code=400, detail="The author name you want to set already exists")

    result = authors_db.update_author_by_id(author_id, author_name)

    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while updating the author")

    return general_responses_models.Message(message="Author updated successfully")


@router.delete("/{author_id}", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
@decorators.author_id_existence_required()
@decorators.author_owner_or_admin_required()
def delete_authors_endpoint(author_id: int, current_user: users_models.User = Depends(get_current_user)):
    result = authors_db.delete_author(author_id)
    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the author")

    return general_responses_models.Message(message="Author deleted successfully")


@router.get("/{author_id}", dependencies=[Depends(get_current_user)], response_model=content_models.Author)
@decorators.user_not_guest_required()
@decorators.author_id_existence_required()
def get_author_by_id_endpoint(author_id: int, current_user: users_models.User = Depends(get_current_user)):
    author = authors_db.get_author_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author


@router.get("", dependencies=[Depends(get_current_user)], response_model=List[content_models.Author])
@decorators.user_not_guest_required()
def get_author_endpoint(current_user: users_models.User = Depends(get_current_user)):
    authors = authors_db.get_authors()
    if not authors:
        raise HTTPException(status_code=404, detail="No authors found")

    return authors


@router.post("", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
def post_authors_endpoint(author_name: str, current_user: users_models.User = Depends(get_current_user)):
    if authors_db.get_author_by_name(author_name):
        raise HTTPException(status_code=400, detail="The author name you want to set already exists")

    result = authors_db.add_author(author_name, current_user.id)
    if not result:
        raise HTTPException(status_code=500, detail="An error occurred while adding the author")

    return general_responses_models.Message(message="Author added successfully")
