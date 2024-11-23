from typing import Union
from models.login import UserSessionModel
from utility.token import decode_jwt
from utility.logging import logger

class USER_TYPE:
    ADMIN = 1
    USER = 2
    GUEST = 3

def get_session(token: str) -> Union[UserSessionModel, None]:
    try:
        data = decode_jwt(token)
        return UserSessionModel(session_id=data["session_id"], user_id=data["user_id"])
    except Exception as e:
        logger.error("Error getting session")
        logger.error(e)
        return None
