import datetime

from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    username: str
    nickname: str
    type: int
    id: int

class UserRegisterModel(BaseModel):
    username: str
    nickname: str
    password: str

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None

class UserLoginModel(BaseModel):
    username: str
    password: str

class FullUserModel(UserModel):
    tags: int
    creators: int
    characters: int
    favorites: int
    content: int
    albums: int
    creation_date: datetime.datetime

class UserPageModel(BaseModel):
    users: list[UserModel]
    total: int
    pages: int
