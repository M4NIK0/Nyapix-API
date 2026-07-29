from pydantic import BaseModel
from typing import List, Optional


class Content(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    author_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class ContentListModel(BaseModel):
    contents: list[Content]
    total_pages: int
    total_contents: int

