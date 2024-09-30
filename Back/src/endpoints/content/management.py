from fastapi import Depends, HTTPException, APIRouter, UploadFile, File
from src.login_management import get_current_user
from src.logs import logger
import src.models.general_responses as general_responses_models
import src.models.users as users_models
import src.decorators as decorators
import src.models.content as content_models
from typing import List
from fastapi import Form, Query
import src.db_management.content.tags as tags_db
import src.db_management.content.authors as authors_db


router = APIRouter()


@router.post("", dependencies=[Depends(get_current_user)], response_model=general_responses_models.Message)
@decorators.user_not_guest_required()
def post_content_endpoint(
        title: str = Form(...),
        description: str = Form(...),
        tags: List[int] = Query(...),
        authors: List[int] = Query(...),
        file: UploadFile = File(...),
        current_user: users_models.User = Depends(get_current_user)
):
    data = content_models.ContentCreation(
        title=title,
        description=description,
        tags=tags,
        authors=authors
    )

    for tag_id in tags:
        if not tags_db.get_tag_by_id(tag_id):
            raise HTTPException(status_code=404, detail="Tag not found")

    for author_id in authors:
        if not authors_db.get_author_by_id(author_id):
            raise HTTPException(status_code=404, detail="Author not found")

    logger.error(f"Content created by user {current_user.username} with data {data.model_dump()}")

    return general_responses_models.Message(message="Content created successfully")
