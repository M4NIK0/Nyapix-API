from src.db_management.connection import get_connection
from src.logs import logger
import src.models.users_history as users_history_models
from typing import Union, List


def get_user_content_history(user_id: int) -> Union[List[users_history_models.UserContentHistory], None]:
    """
    Get the content history of a user
    :param user_id: The ID of the user
    """
    query = "SELECT user_id, content_id, accessed_at, access_type FROM nyapixuser_content_history WHERE user_id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return [users_history_models.UserContentHistory(user_id=result[0], content_id=result[1], action=result[2], timestamp=result[3]) for result in cur.fetchall()]


def get_user_album_history(user_id: int) -> Union[List[users_history_models.UserAlbumHistory], None]:
    """
    Get the album history of a user
    :param user_id: The ID of the user
    """
    query = "SELECT user_id, album_id, accessed_at, access_type FROM nyapixuser_album_history WHERE user_id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            return [users_history_models.UserAlbumHistory(user_id=result[0], album_id=result[1], action=result[2], timestamp=result[3]) for result in cur.fetchall()]
