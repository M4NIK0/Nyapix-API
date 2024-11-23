import utility.users as users_utility
from typing import Union
from utility.logging import logger
import bcrypt

def register(db, username: str, nickname: str, password: str) -> bool:
    """Register a new user in the database, returns True if the user was registered successfully, False otherwise"""
    cursor = db.cursor()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO nyapixuser (username, nickname, password, user_type) VALUES (%s, %s, %s, %s)",
            (username, nickname, password_hash, users_utility.USER_TYPE.GUEST)
        )
        db.commit()
    except Exception as e:
        logger.error(e)
        return False
    finally:
        cursor.close()
    return True

def check_user_exists(db, user: Union[str, int]) -> bool:
    """Check if a user with the given username exists in the database, returns True if the user exists, False otherwise"""
    cursor = db.cursor()
    try:
        if type(user) == str:
            cursor.execute("SELECT * FROM nyapixuser WHERE username = %s", (user,))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        elif type(user) == int:
            cursor.execute("SELECT * FROM nyapixuser WHERE id = %s", (user,))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False
    finally:
        cursor.close()
