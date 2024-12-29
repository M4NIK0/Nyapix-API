from db_management.content import has_user_access, get_content, search_content
from db_management.users import get_user
from models.content import AuthorModel, AuthorPageModel, AlbumPageModel
from models.users import UserModel
from utility.logging import logger
from typing import List, Union
import models.content as models

def is_user_album(db, user_id: int, album_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM nyapixalbum WHERE id = %s", (album_id,))
        result = cursor.fetchone()
        if result is None:
            return False
        return result[0] == user_id
    except Exception as e:
        logger.error("Error checking album ownership")
        logger.error(e)
        return False
    finally:
        cursor.close()

def is_content_in_album(db, album_id: int, content_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT count(*) FROM nyapixalbumcontent WHERE album_id = %s AND content_id = %s", (album_id, content_id))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logger.error("Error checking content in album")
        logger.error(e)
        return False

def add_content_to_album(db, album_id: int, content_id: int) -> bool:
    cursor = db.cursor()
    try:
        if is_content_in_album(db, album_id, content_id):
            return False
        cursor.execute("INSERT INTO nyapixalbumcontent (album_id, content_id) VALUES (%s, %s)", (album_id, content_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding content to album")
        logger.error(e)
        return False
    finally:
        cursor.close()

def remove_content_from_album(db, album_id: int, content_id: int) -> None:
    cursor = db.cursor()
    try:
        if not is_content_in_album(db, album_id, content_id):
            return
        cursor.execute("DELETE FROM nyapixalbumcontent WHERE album_id = %s AND content_id = %s", (album_id, content_id))
        db.commit()
    except Exception as e:
        logger.error("Error removing content from album")
        logger.error(e)
    finally:
        cursor.close()

def add_album(db, user_id: int, info: models.AlbumPostModel) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO nyapixalbum (user_id, title, description) VALUES (%s, %s, %s)", (user_id, info.name, info.description))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding album")
        logger.error(e)
        return False
    finally:
        cursor.close()

def edit_album(db, album_id: int, info: models.AlbumUpdateModel) -> bool:
    cursor = db.cursor()
    try:
        if info.name is not None:
            cursor.execute("UPDATE nyapixalbum SET title = %s WHERE id = %s", (info.name, album_id))
        if info.description is not None:
            cursor.execute("UPDATE nyapixalbum SET description = %s WHERE id = %s", (info.description, album_id))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error updating album")
        logger.error(e)
        return False
    finally:
        cursor.close()

def delete_album(db, album_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM nyapixalbum WHERE id = %s", (album_id,))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error deleting album")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_album(db, user_id: int, album_id: int) -> Union[models.AlbumContentModel, None]:
    cursor = db.cursor()
    try:
        # Get album info
        cursor.execute("SELECT title, description, id FROM nyapixalbum WHERE id = %s", (album_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        info = models.AlbumModel(id=album_id, name=result[0], description=result[1])

        # get album content
        cursor.execute("SELECT content_id FROM nyapixalbumcontent WHERE album_id = %s", (album_id,))
        result = cursor.fetchall()

        contents = [content_id[0] for content_id in result]

        # Remove content user don't have access to
        real_contents = []
        for content_id in contents:
            if has_user_access(db, content_id, user_id):
                real_contents.append(content_id)
        data = [get_content(db, content_id) for content_id in real_contents]

        return models.AlbumContentModel(info=info, contents=data)
    except Exception as e:
        logger.error("Error getting album")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_album_info(db, album_id: int) -> Union[models.AlbumModel, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT title, description FROM nyapixalbum WHERE id = %s", (album_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return models.AlbumModel(id=album_id, name=result[0], description=result[1])
    except Exception as e:
        logger.error("Error getting album info")
        logger.error(e)
        return None
    finally:
        cursor.close()

def get_album_who(db, album_id: int) -> Union[UserModel, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM nyapixalbum WHERE id = %s", (album_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return get_user(db, result[0])
    except Exception as e:
        logger.error("Error getting album owner")
        logger.error(e)
        return None

def get_content_linked_albums(db, content_id: int) -> List[int]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT album_id FROM nyapixalbumcontent WHERE content_id = %s", (content_id,))
        result = cursor.fetchall()
        return [album_id[0] for album_id in result]
    except Exception as e:
        logger.error("Error getting content linked albums")
        logger.error(e)
        return []
    finally:
        cursor.close()

def search_album(db, needed_tags: list[int], needed_characters: list[int], needed_authors: list[int],
                   tags_to_exclude: list[int], characters_to_exclude: list[int], authors_to_exclude: list[int], max_results: int, page: int) -> Union[AlbumPageModel, None]:
    available_content = search_content(db, needed_tags, needed_characters, needed_authors, tags_to_exclude, characters_to_exclude, authors_to_exclude, max_results, page)
    if available_content is None:
        return None

    content_id_dict = {}
    for content in available_content.contents:
        linked_albums = get_content_linked_albums(db, content.id)
        for album_id in linked_albums:
            if album_id not in content_id_dict.keys():
                content_id_dict[album_id] = 0
            content_id_dict[album_id] += 1

    albums = []
    for album_id in content_id_dict.keys():
        album = get_album_info(db, album_id)
        if album is not None:
            albums.append(album)

    total_results = len(albums)
    total_pages = (total_results + max_results - 1) // max_results
    albums = albums[(page - 1) * max_results:page * max_results]

    return AlbumPageModel(albums=albums, total_albums=total_results, total_pages=total_pages)
