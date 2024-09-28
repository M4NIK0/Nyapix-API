from typing import Optional

from pydantic import BaseModel
import datetime


class User(BaseModel):
    id: int
    username: str
    nickname: str
    type: int
    creation_date: datetime.datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None


class BasicUserCreation(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
