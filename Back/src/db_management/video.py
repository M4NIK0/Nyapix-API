import os
from typing import Union

from utility.logging import logger
import bcrypt
import models.users as users_models

def add_video(db, content_id: int, file_path: str) -> bool:
    cursor = db.cursor()
    try:
        total_chunks = len(os.listdir(file_path + ".chunks/"))
        cursor.execute("INSERT INTO nyapixvideo_metadata (content_id, total_chunks) VALUES (%s, %s) RETURNING id", (content_id, total_chunks))
        video_id = cursor.fetchone()[0]

        for i in range(total_chunks):
            with open(file_path + ".chunks/" + "0" * (4 - len(str(i))) + str(i) + ".mp4", "rb") as file:
                data = file.read()
                cursor.execute("INSERT INTO nyapixvideo_chunks (video_id, chunk_number, data) VALUES (%s, %s, %s)", (video_id, i, data))

        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding video")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_chunk(db, video_id: int, chunk_id) -> Union[bytes, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT data FROM nyapixvideo_chunks WHERE video_id = %s AND chunk_number = %s", (video_id, chunk_id))
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        logger.error("Error getting chunks")
        logger.error(e)
        return None
    finally:
        cursor.close()

def add_image(db, content_id: int, file_path: str) -> bool:
    cursor = db.cursor()
    try:
        with open(file_path, "rb") as file:
            data = file.read()
            cursor.execute("INSERT INTO nyapiximage (content_id, data) VALUES (%s, %s)", (content_id, data))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding image")
        logger.error(e)
        return False
    finally:
        cursor.close()
