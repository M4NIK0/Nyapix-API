from pydantic import BaseModel

class SourceModel(BaseModel):
    id: int
    name: str
