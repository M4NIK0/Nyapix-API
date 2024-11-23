import os
import jwt
from typing import Union
from utility.logging import logger

def encode_jwt(data: dict) -> Union[str, None]:
    secret = os.getenv("JWT_SECRET")
    if secret is None:
        raise Exception("JWT_SECRET is not set")
    try:
        return jwt.encode(data, secret, algorithm="HS256")
    except Exception as e:
        logger.error(e)
        return None

def decode_jwt(token: str) -> Union[dict, None]:
    secret = os.getenv("JWT_SECRET")
    if secret is None:
        raise Exception("JWT_SECRET is not set")
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except Exception as e:
        logger.error(e)
        return None
