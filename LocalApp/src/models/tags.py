from pydantic import BaseModel

class Tag(BaseModel):
    id: int
    name: str

class TagListModel(BaseModel):
    tags: list[Tag]
    total_pages: int
    total_tags: int