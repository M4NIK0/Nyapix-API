import os
from typing import Union, List, Tuple

from models.content import ContentModel
from utility.logging import logger
import bcrypt
import models.users as users_models
from utility.media import get_video_length

def add_video(db, content_id: int, file_path) -> bool:
    cursor = db.cursor()
    try:
        with open(file_path, "rb") as file:
            data = file.read()
            cursor.execute("INSERT INTO nyapixvideo (content_id, data) VALUES (%s, %s)", (content_id, data))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding video")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_video(db, content_id: int) -> Union[bytes, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT data FROM nyapixvideo WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        logger.error("Error getting video")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_image(db, content_id: int) -> Union[bytes, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT data FROM nyapiximage WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        logger.error("Error getting image")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_audio(db, content_id: int) -> Union[bytes, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT data FROM nyapixaudio WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        logger.error("Error getting audio")
        logger.error(e)
        return None
    finally:
        cursor.close()

# def add_video(db, content_id: int, file_path: str) -> bool:
#     cursor = db.cursor()
#     try:
#         count chunks
        # total_chunks = len(os.listdir(file_path + ".chunks/"))
        #
        # get video length
        # total_length = 0
        # get_video_length(file_path)
        #
        # current_timecode = 0
        #
        # cursor.execute("INSERT INTO nyapixvideo_metadata (content_id, total_chunks, total_length) VALUES (%s, %s, %s) RETURNING id", (content_id, total_chunks, total_length))
        # video_id = cursor.fetchone()[0]
        #
        # for i in range(total_chunks):
        #     chunk_duration = get_video_length(file_path + ".chunks/" + "0" * (4 - len(str(i))) + str(i) + ".mp4")
        #     with open(file_path + ".chunks/" + "0" * (4 - len(str(i))) + str(i) + ".mp4", "rb") as file:
        #         data = file.read()
        #         cursor.execute("INSERT INTO nyapixvideo_chunks (video_id, chunk_number, data, start_time, end_time) VALUES (%s, %s, %s, %s, %s)", (video_id, i, data, current_timecode, current_timecode + chunk_duration))
        #     current_timecode += chunk_duration
        #
        # db.commit()
        # return True
    # except Exception as e:
    #     logger.error("Error adding video")
    #     logger.error(e)
    #     return False
    # finally:
    #     cursor.close()

# def get_video_chunk(db, video_id: int, chunk_id) -> Union[bytes, None]:
#     cursor = db.cursor()
#     try:
#         cursor.execute("SELECT data FROM nyapixvideo_chunks WHERE video_id = %s AND chunk_number = %s", (video_id, chunk_id))
#         result = cursor.fetchone()
#         return result[0]
#     except Exception as e:
#         logger.error("Error getting chunks")
#         logger.error(e)
#         return None
#     finally:
#         cursor.close()

# def get_video_manifest(db, video_id: int) -> Union[str, None]:
#     cursor = db.cursor()
#     try:
#         cursor.execute("SELECT manifest FROM nyapixvideo_metadata WHERE id = %s", (video_id,))
#         result = cursor.fetchone()
#         return result[0]
#     except Exception as e:
#         logger.error("Error getting video manifest")
#         logger.error(e)
#         return None
#     finally:
#         cursor.close()

# def get_video_total_length(db, video_id: int) -> Union[int, None]:
#     cursor = db.cursor()
#     try:
#         cursor.execute("SELECT total_length FROM nyapixvideo_metadata WHERE id = %s", (video_id,))
#         result = cursor.fetchone()
#         return result[0]
#     except Exception as e:
#         logger.error("Error getting video length")
#         logger.error(e)
#         return None
#     finally:
#         cursor.close()

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

def add_audio(db, content_id: int, file_path: str) -> bool:
    cursor = db.cursor()
    try:
        with open(file_path, "rb") as file:
            data = file.read()
            cursor.execute("INSERT INTO nyapixaudio (content_id, data) VALUES (%s, %s)", (content_id, data))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding audio")
        logger.error(e)
        return False
    finally:
        cursor.close()
