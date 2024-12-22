import models.content as models
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
