from pydantic import BaseModel

class UserContentHistory(BaseModel):
    user_id: int
    content_id: int
    action: int
    timestamp: str

class UserAlbumHistory(BaseModel):
    user_id: int
    album_id: int
    action: int
    timestamp: str
