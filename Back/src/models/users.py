from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    nickname: str
    type: int
    id: int

class UserRegisterModel(BaseModel):
    username: str
    nickname: str
    password: str

class UserLoginModel(BaseModel):
    username: str
    password: str
