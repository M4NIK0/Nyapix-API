import utility.users as users_utility
from typing import Union

from db_management.login import clear_user_sessions
from models.users import FullUserModel, UserUpdateModel
from utility.logging import logger
import bcrypt
import models.users as users_models

def register(db, username: str, nickname: str, password: str) -> bool:
    """Register a new user in the database, returns True if the user was registered successfully, False otherwise"""
    cursor = db.cursor()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        cursor.execute(
            "INSERT INTO nyapixuser (username, nickname, password, user_type) VALUES (%s, %s, %s, %s)",
            (username, nickname, password_hash, users_utility.USER_TYPE.GUEST)
        )
        db.commit()
    except Exception as e:
        logger.error("Error registering user")
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
        logger.error("Error checking user")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_user(db, user: Union[int, str]) -> Union[users_models.UserModel, None]:
    """Returns the user with the given username or id"""
    cursor = db.cursor()
    try:
        if type(user) == str:
            cursor.execute("SELECT nickname, user_type, id FROM nyapixuser WHERE username = %s", (user,))
            result = cursor.fetchone()
            return users_models.UserModel(username=user, nickname=result[0], type=result[1], id=result[2])
        elif type(user) == int:
            cursor.execute("SELECT username, nickname, user_type FROM nyapixuser WHERE id = %s", (user,))
            result = cursor.fetchone()
            return users_models.UserModel(username=result[0], nickname=result[1], type=result[2], id=user)
        else:
            return None
    except Exception as e:
        logger.error("Error getting user")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_full_user(db, user_id: int) -> Union[FullUserModel, None]:
    """Returns the full user model for the given user id"""
    cursor = db.cursor()
    try:
        # Get tags created by user
        cursor.execute("SELECT COUNT(*) FROM nyapixtag WHERE user_id = %s", (user_id,))
        tags = cursor.fetchone()[0]
        # Get authors created by user
        cursor.execute("SELECT COUNT(*) FROM nyapixauthor WHERE user_id = %s", (user_id,))
        authors = cursor.fetchone()[0]
        # Get characters created by user
        cursor.execute("SELECT COUNT(*) FROM nyapixcharacter WHERE user_id = %s", (user_id,))
        characters = cursor.fetchone()[0]
        # Get favorites of the user
        cursor.execute("SELECT COUNT(*) FROM nyapixuser_content_favorites WHERE user_id = %s", (user_id,))
        favorites = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM nyapixuser_album_favorites WHERE user_id = %s", (user_id,))
        favorites += cursor.fetchone()[0]
        # Get content uploaded by user
        cursor.execute("SELECT COUNT(*) FROM nyapixcontent WHERE user_id = %s", (user_id,))
        content = cursor.fetchone()[0]
        # Get albums created by user
        cursor.execute("SELECT COUNT(*) FROM nyapixalbum WHERE user_id = %s", (user_id,))
        albums = cursor.fetchone()[0]
        # Get creation date of user
        cursor.execute("SELECT created_at FROM nyapixuser WHERE id = %s", (user_id,))
        creation_date = cursor.fetchone()[0]

        return FullUserModel(username="Wait", nickname="It is invalid", type=0, id=0, tags=tags, creators=authors, characters=characters, favorites=favorites, content=content, albums=albums, creation_date=creation_date)
    except Exception as e:
        logger.error("Error getting full user")
        logger.error(e)
        return None
    finally:
        cursor.close()

def update_user(db, user: UserUpdateModel, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        if user.username is not None:
            cursor.execute("UPDATE nyapixuser SET username = %s WHERE id = %s", (user.username, user_id))
        if user.nickname is not None:
            cursor.execute("UPDATE nyapixuser SET nickname = %s WHERE id = %s", (user.nickname, user_id))
        if user.password is not None:
            password_hash = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute("UPDATE nyapixuser SET password = %s WHERE id = %s", (password_hash, user_id))
            clear_user_sessions(db, user_id)
        db.commit()
    except Exception as e:
        logger.error("Error updating user")
        logger.error(e)
        return False
    finally:
        cursor.close()
    return True

def delete_user(db, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixuser WHERE id = %s", (user_id,))
        db.commit()
    except Exception as e:
        logger.error("Error deleting user")
        logger.error(e)
        return False
    finally:
        cursor.close()
    return True
