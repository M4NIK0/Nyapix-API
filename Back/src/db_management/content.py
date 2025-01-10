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

        cursor.execute("SELECT id FROM nyapixaudio WHERE content_id = %s", (content_id,))
        result = cursor.fetchone()

        if result is not None:
            to_return.url = f"v1/audio/{result[0]}"

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

def get_content_user_id(db, content_id: int) -> Union[int, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM nyapixcontent WHERE id = %s", (content_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except Exception as e:
        logger.error("Error getting user id from content")
        logger.error(e)
        return None
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

def get_audio_content_id(db, audio_id: int) -> Union[int, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT content_id FROM nyapixaudio WHERE id = %s", (audio_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except Exception as e:
        logger.error("Error getting content id from audio")
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

def has_tag(db, content_id: int, tag_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM nyapixcontent_tag WHERE content_id = %s AND tag_id = %s", (content_id, tag_id))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logger.error("Error checking if content has tag")
        logger.error(e)
        return False
    finally:
        cursor.close()

def has_character(db, content_id: int, character_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM nyapixcontent_characters WHERE content_id = %s AND character_id = %s", (content_id, character_id))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logger.error("Error checking if content has character")
        logger.error(e)
        return False
    finally:
        cursor.close()

def has_author(db, content_id: int, author_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM nyapixcontent_author WHERE content_id = %s AND author_id = %s", (content_id, author_id))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        logger.error("Error checking if content has author")
        logger.error(e)
        return False
    finally:
        cursor.close()

# content = content_db.search_content(db, title_regex, description_regex, needed_tags, needed_characters, needed_authors,
#                                             tags_to_exclude, characters_to_exclude, authors_to_exclude, allowed_sources, max_results, page)
def search_content(db, needed_tags: list[int], needed_characters: list[int], needed_authors: list[int],
                   tags_to_exclude: list[int], characters_to_exclude: list[int], authors_to_exclude: list[int], max_results: int, page: int) -> Union[ContentPageModel, None]:
    cursor = db.cursor()
    try:
        logger.info("Searching using: tags: " + str(needed_tags) + " characters: " + str(needed_characters) + " authors: " + str(needed_authors) + " tags to avoid:" + str(tags_to_exclude) + " characters to exclude: " + str(characters_to_exclude) + " authors to exclude: " + str(authors_to_exclude))

        first_search = "need_tags"
        if len(needed_tags) == 0:
            first_search = "need_characters"
            if len(needed_characters) == 0:
                first_search = "need_authors"
                if len(needed_authors) == 0:
                    return ContentPageModel(contents=[], total_pages=0, total_contents=0)

        content_ids = []
        if first_search == "need_tags":
            # Get all content that have ALL needed tags
            cursor.execute("SELECT content_id FROM nyapixcontent_tag WHERE tag_id = %s", (needed_tags[0],))
            result = cursor.fetchall()
            for row in result:
                add_to_list = True
                for tag_id in needed_tags[1:]:
                    if not has_tag(db, row[0], tag_id):
                        add_to_list = False
                        break
                if add_to_list:
                    content_ids.append(row[0])
        elif first_search == "need_characters":
            # Get all content that have ALL needed characters
            cursor.execute("SELECT content_id FROM nyapixcontent_characters WHERE character_id = %s", (needed_characters[0],))
            result = cursor.fetchall()
            for row in result:
                add_to_list = True
                for character_id in needed_characters[1:]:
                    if not has_character(db, row[0], character_id):
                        add_to_list = False
                        break
                if add_to_list:
                    content_ids.append(row[0])
        elif first_search == "need_authors":
            # Get all content that have ALL needed authors
            cursor.execute("SELECT content_id FROM nyapixcontent_author WHERE author_id = %s", (needed_authors[0],))
            result = cursor.fetchall()
            for row in result:
                add_to_list = True
                for author_id in needed_authors[1:]:
                    if not has_author(db, row[0], author_id):
                        add_to_list = False
                        break
                if add_to_list:
                    content_ids.append(row[0])

        after_forcing_tags = []
        if len(needed_tags) > 0:
            # Remove content that do not have all needed tags
            for item in content_ids:
                add_to_list = True
                for tag_id in needed_tags:
                    if not has_tag(db, item, tag_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_forcing_tags.append(item)
        else:
            after_forcing_tags = content_ids

        logger.info("After forcing tags: " + str(after_forcing_tags))
        after_forcing_characters = []
        if len(needed_characters) > 0:
            # Remove content that do not have all needed characters
            for item in after_forcing_tags:
                add_to_list = True
                for character_id in needed_characters:
                    if not has_character(db, item, character_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_forcing_characters.append(item)
        else:
            after_forcing_characters = after_forcing_tags

        logger.info("After forcing characters: " + str(after_forcing_characters))
        after_forcing_authors = []
        if len(needed_authors) > 0:
            # Remove content that do not have all needed authors
            for item in after_forcing_characters:
                add_to_list = True
                for author_id in needed_authors:
                    if not has_author(db, item, author_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_forcing_authors.append(item)
        else:
            after_forcing_authors = after_forcing_characters
        logger.info("After forcing authors: " + str(after_forcing_authors))

        logger.info("Got content ids: " + str(content_ids))
        after_exclude_tags = []
        if len(tags_to_exclude) > 0:
            # Remove content that have any excluded tags
            for item in after_forcing_authors:
                add_to_list = True
                for tag_id in tags_to_exclude:
                    if has_tag(db, item, tag_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_exclude_tags.append(item)
        else:
            after_exclude_tags = content_ids

        logger.info("After excluding tags: " + str(after_exclude_tags))
        after_exclude_characters = []
        if len(characters_to_exclude) > 0:
            # Remove content that have any excluded characters
            for item in after_exclude_tags:
                add_to_list = True
                for character_id in characters_to_exclude:
                    if has_character(db, item, character_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_exclude_characters.append(item)
        else:
            after_exclude_characters = after_exclude_tags

        logger.info("After excluding characters: " + str(after_exclude_characters))
        after_exclude_authors = after_exclude_characters
        if len(authors_to_exclude) > 0:
            # Remove content that have any excluded authors
            for item in after_exclude_characters:
                add_to_list = True
                for author_id in authors_to_exclude:
                    if has_author(db, item, author_id):
                        add_to_list = False
                        break
                if add_to_list:
                    after_exclude_authors.append(item)
        else:
            after_exclude_authors = after_exclude_characters
        logger.info("After excluding authors: " + str(after_exclude_authors))

        # Remove content that user does not have access to
        after_exclude_authors = [item for item in after_exclude_authors if has_user_access(db, item, 1)]
        logger.info("After excluding access: " + str(after_exclude_authors))

        final_list = [get_content(db, item) for item in after_exclude_authors]

        total = len(final_list)
        total_pages = (total + max_results - 1) // max_results

        logger.info("Final list: " + str(final_list))

        return ContentPageModel(contents=final_list[max_results * (page - 1):max_results * page], total_pages=total_pages, total_contents=total)
    except Exception as e:
        logger.error("Error searching content in db")
        logger.error(e)
        return None
    finally:
        cursor.close()

def add_miniature(db, content_id: int, miniature_path: str) -> bool:
    cursor = db.cursor()
    try:
        with open(miniature_path, "rb") as file:
            cursor.execute("INSERT INTO nyapixminiature (content_id, data) VALUES (%s, %s)", (content_id, file.read()))
        db.commit()
        return True
    except Exception as e:
        logger.error("Error adding miniature")
        logger.error(e)
        return False
    finally:
        cursor.close()

def get_miniature(db, content_id: int) -> Union[bytes, None]:
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM nyapixminiature WHERE content_id = %s", (content_id,))
        result = cursor.fetchone()
        if result[0] == 0:
            with open("./assets/music.png", "rb") as file:
                return file.read()
        cursor.execute("SELECT data FROM nyapixminiature WHERE content_id = %s", (content_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error("Error getting miniature")
        logger.error(e)
        return None
    finally:
        cursor.close()
