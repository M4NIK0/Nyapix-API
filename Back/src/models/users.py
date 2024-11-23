from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    email: str
    id: int

class UserRegisterModel(BaseModel):
    username: str
    nickname: str
    password: str
