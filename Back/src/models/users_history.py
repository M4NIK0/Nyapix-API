from pydantic import BaseModel
import datetime

class UserContentHistory(BaseModel):
    user_id: int
    content_id: int
    action: int
    timestamp: datetime.datetime

class UserAlbumHistory(BaseModel):
    user_id: int
    album_id: int
    action: int
    timestamp: datetime.datetime
