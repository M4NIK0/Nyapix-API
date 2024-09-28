from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str

class Message(BaseModel):
    message: str
