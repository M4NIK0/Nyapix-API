from pydantic import BaseModel
from typing import List, Optional


class Content(BaseModel):
    id: int
    title: str
    description: str
    source: int
    tags: list[int]
    characters: list[int]
    authors: list[int]
    is_private: bool
    url: str


class ContentListModel(BaseModel):
    contents: list[Content]
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

