from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import src.login_management as login_management
import src.models.login as login_models
import src.models.users as user_models
import src.models.general_responses as general_responses
import src.db_management.users.users as users_db
import re


router = APIRouter()


def get_login_form(username: str = Header(...), password: str = Header(...)) -> OAuth2PasswordRequestForm:
    return OAuth2PasswordRequestForm(username=username, password=password)


@router.post(
    "/login", response_model=login_models.Token,
    responses=
    {
        401: {
            "model": general_responses.HTTPError,
            "description": "Invalid credentials", "content":
            {
                "application/json":
                    {
                        "example": {"detail": "InvalidUsername and Password combination."}
                    }
            }
        }
    }
)
def endpoint_login_post(headers: OAuth2PasswordRequestForm = Depends(get_login_form)):
    """Login an employee"""
    login_result = login_management.verify_password(headers.username, headers.password)

    if login_result:
        user = login_management.get_user(headers.username)
        token = login_management.create_access_token(
            data={
                "username": user.username,
                "id": user.id,
                "type": user.type,
                "creation_date": user.creation_date.isoformat(),
                "nickname": user.nickname
            }
        )
        return login_models.Token(access_token=token, token_type="bearer")

    raise HTTPException(status_code=401, detail="Invalid Username and Password combination.")

@router.post(
    "/token", response_model=login_models.Token,
    responses=
    {
        401:
            {
                "model": general_responses.HTTPError,
                "description": "Invalid credentials", "content":
                {
                    "application/json":
                        {
                            "example": {"detail": "Invalid Username and Password combination."}
                        }
                }
            }
    }
)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login for an access token"""
    login_result = login_management.verify_password(form_data.username, form_data.password)

    if login_result:
        user = login_management.get_user(form_data.username)
        token = login_management.create_access_token(
            data={
                "username": user.username,
                "id": user.id,
                "type": user.type,
                "creation_date": user.creation_date.isoformat(),
                "nickname": user.nickname
            }
        )
        return login_models.Token(access_token=token, token_type="bearer")
    raise HTTPException(status_code=401, detail="Invalid Username and Password combination.")


@router.post("/register", response_model=general_responses.Message)
def endpoint_register_post(user: user_models.BasicUserCreation):
    """Register a new user"""
    if users_db.get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    if user.username == "" or not re.match(r"^[a-z0-9_]*$", user.username):
        raise HTTPException(status_code=400, detail="Invalid username")

    users_db.create_user(username=user.username, nickname=user.nickname, hashed_password=login_management.hash_password(user.password), user_type=3)

    return general_responses.Message(message="Account created")
