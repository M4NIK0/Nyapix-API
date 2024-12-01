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
