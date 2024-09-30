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
import hashlib
import magic


router = APIRouter()


def get_random_tmp_filename():
    import random
    import string

    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=50))


def get_file_type(filename: str):
    return magic.Magic(mime=True).from_file(filename)


def check_supported_formats(file_format: str):
    return file_format in ["image/jpeg", "image/png", "image/gif", "video/mp4"]


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

    # Save the file to the server

    filename = get_random_tmp_filename()
    with open(f"/tmp/{filename}", "wb") as buffer:
        buffer.write(file.file.read())

    logger.info(f"File saved as {filename}")

    # Compute SHA256 hash of the file
    with open(f"/tmp/{filename}", "rb") as buffer:
        sha256 = hashlib.sha256()
        sha256.update(buffer.read())
        file_hash = sha256.hexdigest()

    # Check file type
    file_format = get_file_type(f"/tmp/{filename}")
    logger.error(f"File format: {file_format}")

    return general_responses_models.Message(message="Content created successfully")
