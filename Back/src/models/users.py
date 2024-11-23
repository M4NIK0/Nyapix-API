from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    email: str
    id: int
