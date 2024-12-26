from pydantic import BaseModel

class TokenModel(BaseModel):
    access_token: str

class UserSessionModel(BaseModel):
    session_id: int
    user_id: int
