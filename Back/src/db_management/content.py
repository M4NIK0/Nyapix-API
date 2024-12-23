from typing import Union

import models.content as models
from models.content import ContentModel, ContentPageModel
from utility.logging import logger

def add_content(db, content: models.ContentPostModel, file_hash: str, user_id: int) -> int:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixcontent (title, description, source_id, original_file_hash, user_id, is_private) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                          (content.title, content.description, content.source_id, file_hash, user_id, content.is_private))
        content_id = cursor.fetchone()[0]
        for tag_id in content.tags:
            cursor.execute("INSERT INTO nyapixcontent_tag (content_id, tag_id) VALUES (%s, %s)", (content_id, tag_id))
        for character_id in content.characters:
            cursor.execute("INSERT INTO nyapixcontent_characters (content_id, character_id) VALUES (%s, %s)", (content_id, character_id))
        for author_id in content.authors:
            cursor.execute("INSERT INTO nyapixcontent_author (content_id, author_id) VALUES (%s, %s)", (content_id, author_id))
        db.commit()
        return content_id
    except Exception as e:
        logger.error("Error adding content")
        logger.error(e)

        # Remove any leftover data
        try:
            cursor.execute("DELETE FROM nyapixcontent WHERE id = %s", (content_id,))
        except Exception as e:
            pass

        try:
            cursor.execute("DELETE FROM nyapixcontent_tag WHERE content_id = %s", (content_id,))
        except:
            pass

        try:
            cursor.execute("DELETE FROM nyapixcontent_characters WHERE content_id = %s", (content_id,))
        except:
            pass

        try:
            cursor.execute("DELETE FROM nyapixcontent_author WHERE content_id = %s", (content_id,))
        except:
            pass
        db.commit()
        return -1

def update_content(db, content_id: int, data: models.ContentUpdateModel) -> bool:
    cursor = db.cursor()
    try:
        if data.title is not None:
            cursor.execute("UPDATE nyapixcontent SET title = %s WHERE id = %s", (data.title, content_id))
        if data.description is not None:
            cursor.execute("UPDATE nyapixcontent SET description = %s WHERE id = %s", (data.description, content_id))
        if data.source_id is not None:
            cursor.execute("UPDATE nyapixcontent SET source_id = %s WHERE id = %s", (data.source_id, content_id))
        if data.is_private is not None:
            cursor.execute("UPDATE nyapixcontent SET is_private = %s WHERE id = %s", (data.is_private, content_id))
        if data.tags is not None:
            cursor.execute("DELETE FROM nyapixcontent_tag WHERE content_id = %s", (content_id,))
            for tag_id in data.tags:
                cursor.execute("INSERT INTO nyapixcontent_tag (content_id, tag_id) VALUES (%s, %s)", (content_id, tag_id))
        if data.characters is not None:
            cursor.execute("DELETE FROM nyapixcontent_characters WHERE content_id = %s", (content_id,))
            for character_id in data.characters:
                cursor.execute("INSERT INTO nyapixcontent_characters (content_id, character_id) VALUES (%s, %s)", (content_id, character_id))
        if data.authors is not None:
            cursor.execute("DELETE FROM nyapixcontent_author WHERE content_id = %s", (content_id,))
            for author_id in data.authors:
                cursor.execute("INSERT INTO nyapixcontent_author (content_id, author_id) VALUES (%s, %s)", (content_id, author_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error updating content")
        logger.error(e)
        return False

def delete_content(db, content_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixcontent WHERE id = %s", (content_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting content")
        logger.error(e)
        return False

def get_content(db, content_id: int) -> Union[ContentModel, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT title, description, source_id, is_private FROM nyapixcontent WHERE id = %s", (content_id,))
        result = cursor.fetchone()

        if result is None:
            return None

        to_return = ContentModel(title=result[0], description=result[1], is_private=result[3], tags=[], characters=[], authors=[], url="tmp", source=result[2], id=content_id)

        cursor.execute("SELECT tag_id FROM nyapixcontent_tag WHERE content_id = %s", (content_id,))
        result = cursor.fetchall()
        to_return.tags = [tag[0] for tag in result]

        cursor.execute("SELECT character_id FROM nyapixcontent_characters WHERE content_id = %s", (content_id,))
        result = cursor.fetchall()

        to_return.characters = [character[0] for character in result]

        cursor.execute("SELECT author_id FROM nyapixcontent_author WHERE content_id = %s", (content_id,))
        result = cursor.fetchall()

        to_return.authors = [author[0] for author in result]

        # determine if content is video or image
        cursor.execute("SELECT id FROM nyapixvideo WHERE content_id = %s", (content_id,))
        result = cursor.fetchone()

        if result is not None:
            to_return.url = f"v1/video/{result[0]}"

        cursor.execute("SELECT id FROM nyapiximage WHERE content_id = %s", (content_id,))
        result = cursor.fetchone()

        if result is not None:
            to_return.url = f"v1/image/{result[0]}"

        return to_return
    except Exception as e:
        logger.error("Error getting content")
        logger.error(e)
        return None
    finally:
        cursor.close()

def has_user_access(db, content_id: int, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id, is_private FROM nyapixcontent WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        if result is None:
            return False
        if result[0] == user_id:
            return True
        if result[1]:
            return False
        return True
    except Exception as e:
        logger.error("Error checking user access")
        logger.error(e)
        return False
    finally:
        cursor.close()

def is_user_content(db, content_id: int, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM nyapixcontent WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        if result is None:
            return False
        return result[0] == user_id
    except Exception as e:
        logger.error("Error checking user content")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_video_content_id(db, video_id: int) -> Union[int, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT content_id FROM nyapixvideo WHERE id = %s", (video_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except Exception as e:
        logger.error("Error getting content id from video")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_image_content_id(db, image_id: int) -> Union[int, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT content_id FROM nyapiximage WHERE id = %s", (image_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except Exception as e:
        logger.error("Error getting content id from image")
        logger.error(e)
        return None
    finally:
        cursor.close()


def get_user_content(db, user_id: int, max_results: int, page: int) -> Union[ContentPageModel, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM nyapixcontent WHERE user_id = %s", (user_id,))
        total = cursor.fetchone()[0]
        total_pages = (total + max_results - 1) // max_results

        contents = []
        cursor.execute("SELECT id FROM nyapixcontent WHERE user_id = %s ORDER BY id DESC LIMIT %s OFFSET %s", (user_id, max_results, max_results * page))
        result = cursor.fetchall()
        for row in result:
            content = get_content(db, row[0])
            if content is not None:
                contents.append(content)

        return ContentPageModel(contents=contents, total_pages=total_pages, total_contents=total)
    except Exception as e:
        logger.error("Error getting user content from db")
        logger.error(e)
        return None
    finally:
        cursor.close()
