from models.content import AuthorModel, AuthorPageModel
from utility.logging import logger
from typing import List, Union

def search_authors(db, author_name: str, max_results: int) -> AuthorPageModel:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT author_name, id FROM nyapixauthor WHERE author_name LIKE %s ORDER BY author_name LIMIT %s", (f"%{author_name}%", max_results))
        result = cursor.fetchall()
        authors = []
        for row in result:
            authors.append(AuthorModel(name=row[0], id=row[1]))
        return AuthorPageModel(authors=authors, total_authors=len(authors), total_pages=1)
    except Exception as e:
        logger.error("Error searching authors")
        logger.error(e)
        return AuthorPageModel(authors=[], total_authors=0, total_pages=0)
    finally:
        cursor.close()

def get_authors_page(db, page: int, size: int) -> AuthorPageModel:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT author_name, id FROM nyapixauthor ORDER BY author_name LIMIT %s OFFSET %s", (size, (page - 1) * size))
        result = cursor.fetchall()
        authors = []
        for row in result:
            authors.append(AuthorModel(name=row[0], id=row[1]))
        cursor.execute("SELECT COUNT(*) FROM nyapixauthor")
        total = cursor.fetchone()[0]
        total_pages = (total + size - 1) // size  # Corrected page count calculation
        return AuthorPageModel(authors=authors, total_pages=total_pages, total_authors=total)
    except Exception as e:
        logger.error("Error listing authors")
        logger.error(e)
        return AuthorPageModel(authors=[], total_pages=0, total_authors=0)
    finally:
        cursor.close()

def get_author(db, author_id: Union[int, str]) -> Union[AuthorModel, None]:
    cursor = db.cursor()
    try:
        if type(author_id) == int:
            cursor.execute("SELECT author_name FROM nyapixauthor WHERE id = %s", (author_id,))
            result = cursor.fetchone()
            return AuthorModel(name=result[0], id=author_id)
        elif type(author_id) == str:
            cursor.execute("SELECT author_name, id FROM nyapixauthor WHERE author_name = %s", (author_id,))
            result = cursor.fetchone()
            return AuthorModel(name=result[0], id=result[1])
    except Exception as e:
        logger.error("Error getting author")
        logger.error(e)
        return None
    finally:
        cursor.close()

def add_author(db, name: str, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixauthor (author_name, user_id) VALUES (%s, %s)", (name, user_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding author")
        logger.error(e)
        return False
    finally:
        cursor.close()

def delete_author(db, author_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixauthor WHERE id = %s", (author_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting author")
        logger.error(e)
        return False
    finally:
        cursor.close()

def edit_author(db, author_id: int, name: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE nyapixauthor SET author_name = %s WHERE id = %s", (name, author_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error editing author")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_author_by_name(db, author_name: str) -> Union[AuthorModel, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT author_name, id FROM nyapixauthor WHERE author_name = %s", (author_name,))
        result = cursor.fetchone()
        if result is None:
            return None
        return AuthorModel(name=result[0], id=result[1])
    except Exception as e:
        logger.error("Error getting author")
        logger.error(e)
        return None
    finally:
        cursor.close()
