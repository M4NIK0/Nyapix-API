from models.content import CharacterModel, CharacterPageModel
from utility.logging import logger
from typing import List, Union

def search_characters(db, character_name: str, max_results: int) -> CharacterPageModel:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT character_name, id FROM nyapixcharacter WHERE character_name LIKE %s ORDER BY character_name LIMIT %s", (f"%{character_name}%", max_results))
        result = cursor.fetchall()
        characters = []
        for row in result:
            characters.append(CharacterModel(name=row[0], id=row[1]))
        return CharacterPageModel(characters=characters, total_characters=len(characters), total_pages=1)
    except Exception as e:
        logger.error("Error searching characters")
        logger.error(e)
        return CharacterPageModel(characters=[], total_characters=0, total_pages=0)
    finally:
        cursor.close()

def get_characters_page(db, page: int, size: int) -> CharacterPageModel:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT character_name, id FROM nyapixcharacter ORDER BY character_name LIMIT %s OFFSET %s", (size, (page - 1) * size))
        result = cursor.fetchall()
        characters = []
        for row in result:
            characters.append(CharacterModel(name=row[0], id=row[1]))
        cursor.execute("SELECT COUNT(*) FROM nyapixcharacter")
        total = cursor.fetchone()[0]
        total_pages = (total + size - 1) // size  # Corrected page count calculation
        return CharacterPageModel(characters=characters, total_pages=total_pages, total_characters=total)
    except Exception as e:
        logger.error("Error listing characters")
        logger.error(e)
        return CharacterPageModel(characters=[], total_pages=0, total_characters=0)
    finally:
        cursor.close()

def get_character(db, character_id: Union[int, str]) -> Union[CharacterModel, None]:
    cursor = db.cursor()
    try:
        if type(character_id) == int:
            cursor.execute("SELECT character_name FROM nyapixcharacter WHERE id = %s", (character_id,))
            result = cursor.fetchone()
            return CharacterModel(name=result[0], id=character_id)
        elif type(character_id) == str:
            cursor.execute("SELECT character_name, id FROM nyapixcharacter WHERE character_name = %s", (character_id,))
            result = cursor.fetchone()
            return CharacterModel(name=result[0], id=result[1])
    except Exception as e:
        logger.error("Error getting character")
        logger.error(e)
        return None
    finally:
        cursor.close()

def add_character(db, name: str, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixcharacter (character_name, user_id) VALUES (%s, %s)", (name, user_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding character")
        logger.error(e)
        return False
    finally:
        cursor.close()

def delete_character(db, character_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixcharacter WHERE id = %s", (character_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting character")
        logger.error(e)
        return False
    finally:
        cursor.close()

def edit_character(db, character_id: int, name: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE nyapixcharacter SET character_name = %s WHERE id = %s", (name, character_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error editing character")
        logger.error(e)
        return False
    finally:
        cursor.close()
