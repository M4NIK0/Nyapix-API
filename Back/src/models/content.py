from pydantic import BaseModel
import datetime


class Tag(BaseModel):
    id: int
    name: str

class TagInfo(BaseModel):
    id: int
    name: str
    user_id: int
    creation_date: datetime.datetime

class Author(BaseModel):
    id: int
    name: str

class AuthorInfo(BaseModel):
    id: int
    name: str
    user_id: int
    creation_date: datetime.datetime
