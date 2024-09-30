import psycopg2
from typing import Union
from src.db_management.connection import get_connection
import src.models.content as content_models


def check_hash_existence(hash: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM nyapixdata WHERE file_hash = %s", (hash,))
            content = cursor.fetchone()

            if content:
                return True

            return False


def add_content(info: content_models.ContentCreation, file_path: str, file_hash: str, user_id: int, file_format: str) -> Union[int, None]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            with open(file_path, "rb") as file:
                cursor.execute("INSERT INTO nyapixdata (bytes, file_hash, file_format) VALUES (%s, %s, %s) RETURNING id", (psycopg2.Binary(file.read()), file_hash, file_format,))
                connection.commit()
                returned = cursor.fetchone()

                if not returned:
                    return False

                content_id = returned[0]

                cursor.execute("INSERT INTO nyapixcontent (title, description, user_id, data_id) VALUES (%s, %s, %s, %s) RETURNING id", (info.title, info.description, user_id, content_id,))
                connection.commit()
                returned = cursor.fetchone()

                if not returned:
                    return False

                content_id = returned[0]

                for tag in info.tags:
                    cursor.execute("INSERT INTO nyapixcontent_tag (content_id, tag_id) VALUES (%s, %s)", (content_id, tag,))
                    connection.commit()

                for author in info.authors:
                    cursor.execute("INSERT INTO nyapixcontent_author (content_id, author_id) VALUES (%s, %s)", (content_id, author,))
                    connection.commit()

                return content_id
