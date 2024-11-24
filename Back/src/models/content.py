from pydantic import BaseModel

class SourceModel(BaseModel):
    id: int
    name: str

class TagModel(BaseModel):
    id: int
    name: str
