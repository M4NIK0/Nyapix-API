from src.db_management.connection import get_connection
import src.models.content as content_models
from typing import List, Union


def get_authors() -> Union[List[content_models.Author], None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, author_name FROM nyapixauthor")
            authors = cursor.fetchall()

            if authors:
                return [content_models.Author(id=author[0], name=author[1]) for author in authors]

            return None


def add_author(author_name: str, user_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO nyapixauthor (author_name, user_id) VALUES (%s, %s)", (author_name, user_id,))
            connection.commit()

            return True


def get_author_by_id(author_id: int) -> Union[content_models.Author, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, author_name FROM nyapixauthor WHERE id = %s", (author_id,))
            author = cursor.fetchone()

            if author:
                return content_models.Author(id=author[0], name=author[1])

            return None


def get_author_by_name(author_name: str) -> Union[content_models.Author, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, author_name FROM nyapixauthor WHERE author_name = %s", (author_name,))
            author = cursor.fetchone()

            if author:
                return content_models.Author(id=author[0], name=author[1])

            return None


def get_author_info_by_id(author_id: int) -> Union[content_models.AuthorInfo, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, author_name, user_id, created_at FROM nyapixauthor WHERE id = %s", (author_id,))
            author = cursor.fetchone()

            if author:
                return content_models.AuthorInfo(id=author[0], name=author[1], user_id=author[2], creation_date=author[3])

            return None


def update_author_by_id(author_id: int, author_name: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE nyapixauthor SET author_name = %s WHERE id = %s", (author_name, author_id,))
            connection.commit()

            return True


def delete_author(author_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM nyapixauthor WHERE id = %s", (author_id,))
            connection.commit()

            return True


def search_authors(string: str) -> List[content_models.Author]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, author_name FROM nyapixauthor WHERE author_name LIKE %s", (f"%{string}%",))
            authors = cursor.fetchall()

            if authors:
                return [content_models.Author(id=author[0], name=author[1]) for author in authors]

            return None
