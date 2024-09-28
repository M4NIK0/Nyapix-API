from typing import Union
from typing import List
import src.models.users as users_models
import src.db_management.connection as db_connection


def get_password_hash_by_nickname(username: str) -> Union[str, None]:
    """
    Get the password hash of a user
    :param username: The nickname of the user
    """
    query = "SELECT password FROM nyapixuser WHERE username = %s"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            return cur.fetchone()[0] if cur.rowcount else None


def get_user_by_username(username: str) -> Union[users_models.User, None]:
    """&
    Get a user by username
    :param username: The username of the user
    """
    query = "SELECT id, username, nickname, user_type, created_at FROM nyapixuser WHERE username = %s"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            result = cur.fetchone()
            if result:
                return users_models.User(id=result[0], username=result[1], nickname=result[2], type=result[3], creation_date=result[4])
            return None


def get_users_list() -> List[users_models.User]:
    """
    Get all users
    """
    query = "SELECT id, username, nickname, user_type, created_at FROM nyapixuser"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [users_models.User(id=result[0], username=result[1], nickname=result[2], type=result[3], creation_date=result[4]) for result in cur.fetchall()]


def get_user_by_id(user_id: int) -> Union[users_models.User, None]:
    """
    Get a user by ID
    :param user_id: The ID of the user
    """
    query = "SELECT id, username, nickname, user_type, created_at FROM nyapixuser WHERE id = %s"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            result = cur.fetchone()
            if result:
                return users_models.User(id=result[0], username=result[1], nickname=result[2], type=result[3], creation_date=result[4])
            return None


def create_user(username: str, nickname: str, hashed_password: str, user_type: int) -> Union[users_models.User, None]:
    """
    Create a user
    :param nickname: The nickname of the user
    :param username: The username of the user
    :param hashed_password: The hashed password of the user (NEVER PUT THE PLAIN TEXT PASSWORD IN THE DATABASE PLEASE)
    :param user_type: The type of the user (almost always 'user', sometimes 'admin')
    :return:
    """
    query = "INSERT INTO nyapixuser (nickname, username, password, user_type) VALUES (%s, %s, %s, %s) RETURNING id, created_at"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, nickname, hashed_password, user_type))
            result = cur.fetchone()
            if result:
                return users_models.User(id=result[0], username=username, nickname=nickname, type=user_type, creation_date=result[1])
            return None


def update_user(user_id: int, nickname: str = None, username: str = None, hashed_password: str = None, user_type: str = None) -> Union[users_models.User, None]:
    """
    Edit a user
    :param user_id: The ID of the user
    :param nickname: The nickname of the user
    :param username: The username of the user
    :param hashed_password: The hashed password of the user (NEVER PUT THE PLAIN TEXT PASSWORD IN THE DATABASE PLEASE)
    :param user_type: The type of the user (almost always 'user', sometimes 'admin')
    :return:
    """
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            if hashed_password:
                query = "UPDATE nyapixuser SET password = %s WHERE id = %s"
                cur.execute(query, (hashed_password, user_id))
            if nickname:
                query = "UPDATE nyapixuser SET nickname = %s WHERE id = %s"
                cur.execute(query, (nickname, user_id))
            if username:
                query = "UPDATE nyapixuser SET username = %s WHERE id = %s"
                cur.execute(query, (username, user_id))
            if user_type:
                query = "UPDATE nyapixuser SET user_type = %s WHERE id = %s"
                cur.execute(query, (user_type, user_id))
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> bool:
    """
    Delete a user
    :param user_id: The ID of the user
    """
    query = "DELETE FROM nyapixuser WHERE id = %s"
    with db_connection.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return cur.rowcount > 0
