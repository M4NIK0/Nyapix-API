from pydantic import BaseModel
import datetime
from typing import List
from fastapi import UploadFile


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

class ContentDescription(BaseModel):
    id: int
    title: str
    description: str
    uploader_nickname: str
    tags: List[str]
    authors: List[str]
    creation_date: datetime.datetime

class ContentCreation(BaseModel):
    title: str
    description: str
    tags: List[int]
    authors: List[int]
