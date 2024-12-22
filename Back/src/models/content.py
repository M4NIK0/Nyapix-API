import datetime

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
