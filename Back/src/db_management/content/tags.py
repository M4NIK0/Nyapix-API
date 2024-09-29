from src.db_management.connection import get_connection
import src.models.content as content_models
from typing import List, Union


def get_tags() -> Union[List[content_models.Tag], None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, tag_name FROM nyapixtag")
            tags = cursor.fetchall()

            if tags:
                return [content_models.Tag(id=tag[0], name=tag[1]) for tag in tags]

            return None


def add_tag(tag_name: str, user_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO nyapixtag (tag_name, user_id) VALUES (%s, %s)", (tag_name, user_id,))
            connection.commit()

            return True


def get_tag_by_id(tag_id: int) -> Union[content_models.Tag, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, tag_name FROM nyapixtag WHERE id = %s", (tag_id,))
            tag = cursor.fetchone()

            if tag:
                return content_models.Tag(id=tag[0], name=tag[1])

            return None


def get_tag_by_name(tag_name: str) -> Union[content_models.Tag, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, tag_name FROM nyapixtag WHERE tag_name = %s", (tag_name,))
            tag = cursor.fetchone()

            if tag:
                return content_models.Tag(id=tag[0], name=tag[1])

            return None


def get_tag_info_by_id(tag_id: int) -> Union[content_models.TagInfo, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, tag_name, user_id, created_at FROM nyapixtag WHERE id = %s", (tag_id,))
            tag = cursor.fetchone()

            if tag:
                return content_models.TagInfo(id=tag[0], name=tag[1], user_id=tag[2], creation_date=tag[3])

            return None


def delete_tag(tag_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM nyapixtag WHERE id = %s", (tag_id,))
            connection.commit()
            return True


def update_tag_by_id(tag_id: int, tag_name: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE nyapixtag SET tag_name = %s WHERE id = %s", (tag_name, tag_id,))
            connection.commit()
            return True
