import datetime
from typing import Union, Optional

from pydantic import BaseModel

class SourceModel(BaseModel):
    id: int
    name: str

class TagModel(BaseModel):
    id: int
    name: str

class CompleteTagModel(TagModel):
    user_id: int
    creation_date: datetime.datetime

class TagPageModel(BaseModel):
    tags: list[TagModel]
    total_pages: int
    total_tags: int

class CharacterModel(BaseModel):
    id: int
    name: str

class CharacterPageModel(BaseModel):
    characters: list[CharacterModel]
    total_pages: int
    total_characters: int

class AuthorModel(BaseModel):
    id: int
    name: str

class AuthorPageModel(BaseModel):
    authors: list[AuthorModel]
    total_pages: int
    total_authors: int

class ContentModel(BaseModel):
    id: int
    title: str
    description: str
    source: int
    tags: list[TagModel]
    characters: list[CharacterModel]
    authors: list[AuthorModel]
    is_private: bool
    url: str

class ContentPageModel(BaseModel):
    contents: list[ContentModel]
    total_pages: int
    total_contents: int

class ContentPostModel(BaseModel):
    title: str
    description: str
    source_id: int
    tags: list[int]
    characters: list[int]
    authors: list[int]
    is_private: bool

class ContentUpdateModel(BaseModel):
    title: Optional[str]
    description: Optional[str]
    source_id: Optional[int]
    tags: Optional[list[int]]
    characters: Optional[list[int]]
    authors: Optional[list[int]]
    is_private: Optional[bool]
