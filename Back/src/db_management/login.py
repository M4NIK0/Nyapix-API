from utility.logging import logger
from utility.token import encode_jwt, decode_jwt
from typing import Union
import models.users as users_models
import models.login as login_models
import bcrypt

def create_session(db, user_id: int) -> str:
    """Returns the session token"""
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixuser_session (user_id) VALUES (%s) RETURNING id", (user_id,))
        session_id = cursor.fetchone()[0]
        db.commit()
        token = encode_jwt({"session_id": session_id, "user_id": user_id})
        return token
    except Exception as e:
        logger.error("Error creating session")
        raise e
    finally:
        cursor.close()

def delete_session(db, token: str) -> bool:
    """Returns True if the session was deleted successfully, False otherwise"""
    cursor = db.cursor()
    try:
        data = decode_jwt(token)
        cursor.execute("DELETE FROM nyapixuser_session WHERE id = %s", (data["session_id"],))
        db.commit()
    except Exception as e:
        logger.error("Error deleting session")
        logger.error(e)
        return False
    finally:
        cursor.close()
    return True

def check_session(db, token: str) -> bool:
    """Returns True if the session exists, False otherwise"""
    cursor = db.cursor()
    try:
        data = decode_jwt(token)
        cursor.execute("SELECT * FROM nyapixuser_session WHERE id = %s", (data["session_id"],))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logger.error("Error checking session")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_session_user(db, token: str) -> Union[users_models.UserModel, None]:
    """Returns the user associated with the session"""
    cursor = db.cursor()
    try:
        data = decode_jwt(token)
        cursor.execute("SELECT username, nickname, user_type FROM nyapixuser WHERE id = %s", (data["user_id"],))
        result = cursor.fetchone()
        return users_models.UserModel(username=result[0], nickname=result[1], type=result[2], id=data["user_id"])
    except Exception as e:
        logger.error("Error getting user from session")
        logger.error(e)
        return None
    finally:
        cursor.close()

def check_user_login(db, username: str, password: str) -> bool:
    """Returns the token if the login is successful, None otherwise"""
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, password FROM nyapixuser WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result is None:
            return False
        if bcrypt.checkpw(password.encode("utf-8"), result[1].encode("utf-8")):
            return True
        return False
    except Exception as e:
        logger.error("Error checking user login")
        logger.error(e)
        return False
    finally:
        cursor.close()
