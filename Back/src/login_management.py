import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from os import getenv
from src.logs import logger
import bcrypt
import src.models.users as users_models
import src.db_management.users as db_user

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """Hash a password"""
    b = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b, salt)
    return hashed.decode('utf-8')


def verify_password(username: str, password: str) -> bool:
    """
    Verify a password
    :param username: The username of the user
    :param password: The password to be verified
    """
    stored_password = db_user.get_password_hash_by_nickname(username)
    if not stored_password:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))


def get_user(username: str) -> Union[users_models.User, None]:
    """
    Get a user by username
    :param username: The username of the user
    """
    return db_user.get_user_by_username(username)

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create an access token
    :param data: The data to be included in the token
    :param expires_delta: The expiration time of the token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, getenv("SECRET_KEY"), algorithm=getenv("ALGORITHM"))
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> users_models.User:
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        return users_models.User(id=payload.get("id"), username=payload.get("username"), type=payload.get("type"), creation_date=payload.get("creation_date"), nickname=payload.get("nickname"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
