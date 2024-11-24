from models.content import SourceModel
from utility.logging import logger
from typing import List, Union


def list_sources(db) -> List[SourceModel]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT name, id FROM nyapixcontent_sources")
        result = cursor.fetchall()
        sources = []
        for row in result:
            sources.append(SourceModel(name=row[0], id=row[1]))
        return sources
    except Exception as e:
        logger.error("Error listing sources")
        logger.error(e)
        return []
    finally:
        cursor.close()

def get_source(db, source: Union[int, str]) -> Union[SourceModel, None]:
    cursor = db.cursor()
    try:
        if type(source) == str:
            cursor.execute("SELECT name, id FROM nyapixcontent_sources WHERE name = %s", (source,))
            result = cursor.fetchone()
            return SourceModel(name=result[0], id=result[1])
        elif type(source) == int:
            cursor.execute("SELECT name, id FROM nyapixcontent_sources WHERE id = %s", (source,))
            result = cursor.fetchone()
            return SourceModel(name=result[0], id=result[1])
        else:
            return None
    except Exception as e:
        logger.error("Error getting source")
        logger.error(e)
        return None

def add_source(db, name: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixcontent_sources (name) VALUES (%s)", (name,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding source")
        logger.error(e)
        return False
    finally:
        cursor.close()

def delete_source(db, source_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixcontent_sources WHERE id = %s", (source_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting source")
        logger.error(e)
        return False
    finally:
        cursor.close()

def edit_source(db, source_id: int, name: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE nyapixcontent_sources SET name = %s WHERE id = %s", (name, source_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error updating source")
        logger.error(e)
        return False
    finally:
        cursor.close()
