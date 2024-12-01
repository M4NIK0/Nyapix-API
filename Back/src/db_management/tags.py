from models.content import SourceModel, TagModel, TagPageModel
from utility.logging import logger
from typing import List, Union

def list_tags(db) -> List[TagModel]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT tag_name, id FROM nyapixtag")
        result = cursor.fetchall()
        tags = []
        for row in result:
            tags.append(TagModel(name=row[0], id=row[1]))
        return tags
    except Exception as e:
        logger.error("Error listing sources")
        logger.error(e)
        return []
    finally:
        cursor.close()

def get_tags_page(db, page: int, size: int) -> TagPageModel:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT tag_name, id FROM nyapixtag ORDER BY tag_name LIMIT %s OFFSET %s", (size, (page - 1) * size))
        result = cursor.fetchall()
        tags = []
        for row in result:
            tags.append(TagModel(name=row[0], id=row[1]))
        cursor.execute("SELECT COUNT(*) FROM nyapixtag")
        total = cursor.fetchone()[0]
        total_pages = (total + size - 1) // size  # Corrected page count calculation
        return TagPageModel(tags=tags, total_pages=total_pages, total_tags=total)
    except Exception as e:
        logger.error("Error listing sources")
        logger.error(e)
        return TagPageModel(tags=[], total_pages=0, total_tags=0)
    finally:
        cursor.close()

def get_tag(db, source: Union[int, str]) -> Union[TagModel, None]:
    cursor = db.cursor()
    try:
        if type(source) == str:
            cursor.execute("SELECT tag_name, id FROM nyapixtag WHERE tag_name = %s", (source,))
            result = cursor.fetchone()
            return TagModel(name=result[0], id=result[1])
        elif type(source) == int:
            cursor.execute("SELECT tag_name, id FROM nyapixtag WHERE id = %s", (source,))
            result = cursor.fetchone()
            return TagModel(name=result[0], id=result[1])
        else:
            return None
    except Exception as e:
        logger.error("Error getting source")
        logger.error(e)
        return None

def add_tag(db, name: str, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixtag (tag_name, user_id) VALUES (%s, %s)", (name, user_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding source")
        logger.error(e)
        return False
    finally:
        cursor.close()

def delete_source(db, tag_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixtag WHERE id = %s", (tag_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting source")
        logger.error(e)
        return False
    finally:
        cursor.close()

def edit_tag(db, tag_id: int, name: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE nyapixtag SET tag_name = %s WHERE id = %s", (name, tag_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error updating source")
        logger.error(e)
        return False
    finally:
        cursor.close()

def chek_is_user_tag(db, user_id, tag_id) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM nyapixtag WHERE user_id = %s AND id = %s", (user_id, tag_id))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logger.error("Error checking user tag")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_user_tags(db, user_id) -> List[TagModel]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT tag_name, id FROM nyapixtag WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        tags = []
        for row in result:
            tags.append(TagModel(name=row[0], id=row[1]))
        return tags
    except Exception as e:
        logger.error("Error getting user tags")
        logger.error(e)
        return []
    finally:
        cursor.close()
