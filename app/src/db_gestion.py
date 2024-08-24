import sqlite3
import os
from typing import Set, Dict, List, Any

import hashlib


def connect_db(filename: str, logger) -> sqlite3.Connection:
    db = None
    filename = f"data/{filename}"
    try:
        db = sqlite3.connect(filename)
        logger.info(f"Connected to database {filename}")
        return db
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database {filename}: {e}")


def create_table(db: sqlite3.Connection, table_name: str, columns: list, logger) -> bool:
    try:
        cursor = db.cursor()
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(columns)})")
        db.commit()
        logger.info(f"Table {table_name} created.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error creating table {table_name}: {e}")
        return False


def put_data(db: sqlite3.Connection, table_name: str, data: dict, logger) -> bool:
    try:
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join(data.values())})")
        db.commit()
        logger.info(f"Data inserted into {table_name}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error inserting data into {table_name}: {e}")
        return False


def create_content_tables(db: sqlite3.Connection, logger) -> bool:
    '''Create the content tables in the database.'''
    try:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE Item (id INTEGER PRIMARY KEY, name TEXT, path TEXT, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE Tag (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE ItemTag (ItemId INTEGER, TagId INTEGER)")
        cursor.execute("CREATE TABLE Author (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE ItemAuthor (ItemId INTEGER, AuthorId INTEGER)")
        db.commit()
        logger.info("Content tables created.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error creating table content: {e}")
        return False


def check_content_tables(db: sqlite3.Connection, logger) -> bool:
    '''Check if the content tables exist in the database.'''
    try:
        cursor = db.cursor()
        if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Item'").fetchone():
            return False
        if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Tag'").fetchone():
            return False
        if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTag'").fetchone():
            return False
        if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Author'").fetchone():
            return False
        if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemAuthor'").fetchone():
            return False
        return True
    except sqlite3.Error as e:
        logger.error(f"Error checking content tables: {e}")
        return False


def get_taglist(db: sqlite3.Connection, logger) -> list:
    """Get the list of tags from the database."""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Tag")
        tags = cursor.fetchall()
        cursor.execute("SELECT id FROM Tag")
        ids = cursor.fetchall()
        tagsdata = []

        for i in range(len(tags)):
            newtag = {"name": tags[i][0], "id": ids[i][0]}
            tagsdata.append(newtag)

        return tagsdata
    except sqlite3.Error as e:
        logger.error(f"Error getting tag list: {e}")


def add_tag(db: sqlite3.Connection, tag: str, logger) -> bool:
    """Add a tag to the database."""
    tag = tag.lower()
    try:
        for t in get_taglist(db, logger):
            if t['name'] == tag:
                logger.error(f"Tag {tag} already exists.")
                return True

        cursor = db.cursor()
        cursor.execute(f"INSERT INTO Tag (name) VALUES ('{tag}')")
        db.commit()
        logger.info(f"Tag {tag} added.")

        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding tag {tag}: {e}")
        return False


def edit_tag(db: sqlite3.Connection, tag_id: int, new_name: str, logger) -> bool:
    """Edit a tag in the database."""
    try:
        cursor = db.cursor()
        cursor.execute(f"UPDATE Tag SET name = '{new_name}' WHERE id = {tag_id}")
        db.commit()
        logger.info(f"Tag {tag_id} edited with new name {new_name}.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error editing tag {tag_id}: {e}")
        return False


def remove_tag(db: sqlite3.Connection, tag: str, logger) -> bool:
    '''Remove a tag from the database.'''
    tag = tag.lower()
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id FROM Tag WHERE name = '{tag}'")
        tag_id = cursor.fetchone()
        if tag_id is None:
            logger.error(f"Tag {tag} not found.")
            return False
        tag_id = tag_id[0]
        cursor.execute(f"DELETE FROM Tag WHERE id = {tag_id}")
        db.commit()
        cursor.execute(f"DELETE FROM ItemTag WHERE TagId = {tag_id}")
        db.commit()
        logger.info(f"Tag {tag} removed.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error removing tag {tag}: {e}")
        return False


def get_item_tags(db: sqlite3.Connection, item_id: int, logger) -> list:
    '''Get the tags of an item from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT TagId FROM ItemTag WHERE ItemId = {item_id}")
        tags = cursor.fetchall()
        tagsdata = []
        for i in range(len(tags)):
            tagsdata.append(tags[i][0])

        logger.info(f"Got tags for item {item_id}: {tagsdata}")
        return tagsdata
    except sqlite3.Error as e:
        logger.error(f"Error getting tags for item {item_id}: {e}")


def get_item(db: sqlite3.Connection, item_id: int, logger) -> dict:
    '''Get an item from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM Item WHERE id = {item_id}")
        item = cursor.fetchone()
        if item is None:
            logger.error(f"Item {item_id} not found.")
            return None
        return {"id": item[0], "name": item[1], "path": item[2], "extension": item[2].split('.')[-1], "size": os.path.getsize(item[2]) if os.path.exists(item[2]) else 0, "tags": [get_tag_name(db, tag, logger) for tag in get_item_tags(db, item_id, logger)]}
    except sqlite3.Error as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return None


def get_tag_name(db: sqlite3.Connection, tag_id: int, logger) -> str:
    '''Get the name of a tag from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT name FROM Tag WHERE id = {tag_id}")
        tag = cursor.fetchone()
        if tag is None:
            logger.error(f"Tag {tag_id} not found.")
            return None
        return tag[0]
    except sqlite3.Error as e:
        logger.error(f"Error getting tag {tag_id}: {e}")
        return None


def get_tag_id(db: sqlite3.Connection, tag_name: str, logger) -> int:
    '''Get the ID of a tag from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id FROM Tag WHERE name = '{tag_name}'")
        tag = cursor.fetchone()
        if tag is None:
            logger.error(f"Tag {tag_name} not found.")
            return None
        return tag[0]
    except sqlite3.Error as e:
        logger.error(f"Error getting tag {tag_name}: {e}")
        return None


def get_items_with_tags(db: sqlite3.Connection, tags: list, logger) -> list:
    '''Get only items that have all the specified tags from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT ItemId FROM ItemTag WHERE TagId IN ({', '.join([str(get_tag_id(db, tag, logger)) for tag in tags])})")
        item_ids = cursor.fetchall()
        items = []
        for item_id in item_ids:
            new_item = get_item(db, item_id[0], logger)
            if new_item is not None:
                to_add = True
                for tag in tags:
                    if tag not in new_item['tags']:
                        to_add = False
                        break
                if to_add and new_item not in items:
                    items.append(new_item)

        logger.info(f"Got {len(items)} items with tags {tags}.")
        return items
    except sqlite3.Error as e:
        logger.error(f"Error getting items with tags {tags}: {e}")
        return []


def add_item(db: sqlite3.Connection, item: dict, logger) -> dict:
    """Add an item to the database."""
    try:
        cursor = db.cursor()
        tag_ids = []
        for tag in item['tags']:
            cursor.execute(f"SELECT id FROM Tag WHERE name = '{tag}'")
            tag_id = cursor.fetchone()
            if tag_id is None:
                logger.error(f"Tag {tag} not found.")
                return {"id": None, "success": False, "error": f"Tag {tag} not found."}
            tag_id = tag_id[0]
            tag_ids.append(tag_id)
        cursor.execute(f"INSERT INTO Item (name, path) VALUES ('{item['name']}', '{item['path']}')")
        db.commit()
        cursor.execute(f"SELECT id FROM Item WHERE name = '{item['name']}' AND path = '{item['path']}'")
        item_id = cursor.lastrowid

        for tag_id in tag_ids:
            cursor.execute(f"INSERT INTO ItemTag (ItemId, TagId) VALUES ({item_id}, {tag_id})")
            db.commit()

        logger.info(f"Item {item['name']} added.")
        return {"id": item_id, "success": True}
    except sqlite3.Error as e:
        logger.error(f"Error adding item {item['name']}: {e}")
        return {"id": None, "success": False, "error": f"{e}"}


def remove_item(db: sqlite3.Connection, item_id: int, logger) -> bool:
    """Remove an item from the database."""
    try:
        cursor = db.cursor()
        item = get_item(db, item_id, logger)

        if item is None:
            logger.error(f"Item {item_id} not found.")
            return False

        item_file_path = item['path']
        item_thumb_path = "data/nyapix_content/thumbs/" + item_file_path.split("/")[-1].split(".")[0] + ".png"
        if item_file_path is None or not os.path.exists(item_file_path):
            logger.error(f"Item {item_id} not found.")
        else:
            os.remove(item_file_path)
            logger.info(f"Item {item_id} file removed.")
        if item_thumb_path is None or not os.path.exists(item_thumb_path):
            logger.error(f"Item {item_id} thumb not found.")
        else:
            os.remove(item_thumb_path)
            logger.info(f"Item {item_id} thumb removed.")

        cursor.execute(f"DELETE FROM Item WHERE id = {item_id}")
        db.commit()
        cursor.execute(f"DELETE FROM ItemTag WHERE ItemId = {item_id}")
        db.commit()
        logger.info(f"Item {item_id} removed.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error removing item {item_id}: {e}")
        return False


def edititem(db: sqlite3.Connection, item_id: int, name: str, tags: list, logger) -> bool:
    '''Edit an item in the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"UPDATE Item SET name = '{name}' WHERE id = {item_id}")
        db.commit()
        cursor.execute(f"DELETE FROM ItemTag WHERE ItemId = {item_id}")
        db.commit()
        for tag in tags:
            cursor.execute(f"SELECT id FROM Tag WHERE name = '{tag}'")
            tag_id = cursor.fetchone()
            if tag_id is None:
                logger.error(f"Tag {tag} not found.")
                return False
            tag_id = tag_id[0]
            cursor.execute(f"INSERT INTO ItemTag (ItemId, TagId) VALUES ({item_id}, {tag_id})")
            db.commit()

        logger.info(f"Item {item_id} edited.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error editing item {item_id}: {e}")
        return False


def purge_non_existing(db: sqlite3.Connection, logger) -> bool:
    '''Purge items that have no existing tags from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM Item")
        items = cursor.fetchall()
        for item in items:
            cursor.execute(f"SELECT path FROM Item WHERE id = {item[0]}")
            item_path = cursor.fetchone()[0]
            if not os.path.exists(item_path):
                remove_item(db, item[0], logger)

        logger.info("Non-existing items purged.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error purging non-existing items: {e}")
        return False


def get_tags_statistics(db: sqlite3.Connection, logger) -> dict:
    try:
        cursor = db.cursor()
        # Initialize a dictionary to hold tag counts
        tag_counts = {}

        # Get all tags and their IDs
        cursor.execute("SELECT id, name FROM Tag")
        all_tags = cursor.fetchall()

        # Calculate the count of each tag across all items
        for tag_id, tag_name in all_tags:
            cursor.execute("SELECT COUNT(*) FROM ItemTag WHERE TagId = ?", (tag_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                tag_counts[tag_name] = count

        # Prepare the tagsdata dictionary
        tagsdata = {"used": [], "unused": [], "total": 0, "error": None}

        # Populate the used and unused lists
        for tag_id, tag_name in all_tags:
            if tag_name in tag_counts:
                tagsdata["used"].append({"name": tag_name, "count": tag_counts[tag_name]})
            else:
                tagsdata["unused"].append(tag_name)

        tagsdata["total"] = len(tagsdata["used"]) + len(tagsdata["unused"])

        images_stats = get_images_statistics(db, logger)

        result = {"images": {"total": images_stats["images"], "size": images_stats["size"]}, "tags": tagsdata, "error": None, "success": True}

        logger.info(f"Got tags statistics: {result}")
        return result
    except sqlite3.Error as e:
        logger.error(f"Error getting tags statistics: {e}")
        return {"images": {"total": 0, "size": 0}, "tags": {"used": [], "unused": [], "total": 0}, "error": f"{e}", "success": False}


def get_images_statistics(db: sqlite3.Connection, logger) -> dict:
    try:
        cursor = db.cursor()
        # Initialize a dictionary to hold image counts
        image_counts = {}

        # Get all images and their IDs
        cursor.execute("SELECT id, path FROM Item")
        all_images = cursor.fetchall()

        # get all content size
        size = 0
        for image_id, image_path in all_images:
            if os.path.exists(image_path):
                size += os.path.getsize(image_path)

        # Calculate the count of each image across all tags
        result = {"images": len(all_images), "size": size, "error": None}
        logger.info(f"Got images statistics: {result}")
        return result

    except sqlite3.Error as e:
        logger.error(f"Error getting images statistics: {e}")
        return {"images": 0, "size": 0, "error": f"{e}"}


def get_authorslist(db: sqlite3.Connection, logger) -> list:
    """Get the list of authors from the database."""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Author")
        authors = cursor.fetchall()
        cursor.execute("SELECT id FROM Author")
        ids = cursor.fetchall()
        authorsdata = []

        for i in range(len(authors)):
            newauthor = {"name": authors[i][0], "id": ids[i][0]}
            authorsdata.append(newauthor)

        return authorsdata
    except sqlite3.Error as e:
        logger.error(f"Error getting authors list: {e}")


def get_author_id(db: sqlite3.Connection, author_name: str, logger) -> int:
    '''Get the ID of an author from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id FROM Author WHERE name = '{author_name}'")
        author = cursor.fetchone()
        if author is None:
            logger.error(f"Author {author_name} not found.")
            return None
        return author[0]
    except sqlite3.Error as e:
        logger.error(f"Error getting author {author_name}: {e}")
        return None


def add_author(db: sqlite3.Connection, author: str, logger) -> bool:
    """Add an author to the database."""
    author = author.lower()
    try:
        for a in get_authorslist(db, logger):
            if a['name'] == author:
                logger.error(f"Author {author} already exists.")
                return True

        cursor = db.cursor()
        cursor.execute(f"INSERT INTO Author (name) VALUES ('{author}')")
        db.commit()
        logger.info(f"Author {author} added.")

        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding author {author}: {e}")
        return False


def edit_author(db: sqlite3.Connection, author_id: int, new_name: str, logger) -> bool:
    """Edit an author in the database."""
    try:
        cursor = db.cursor()
        if get_author_id(db, new_name, logger) is not None:
            logger.error(f"Author {new_name} already exists.")
            return False
        cursor.execute(f"UPDATE Author SET name = '{new_name}' WHERE id = {author_id}")
        db.commit()
        logger.info(f"Author {author_id} edited with new name {new_name}.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error editing author {author_id}: {e}")
        return False


def remove_author(db: sqlite3.Connection, author: str, logger) -> bool:
    '''Remove an author from the database.'''
    author = author.lower()
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT id FROM Author WHERE name = '{author}'")
        author_id = cursor.fetchone()
        if author_id is None:
            logger.error(f"Author {author} not found.")
            return False
        author_id = author_id[0]
        cursor.execute(f"DELETE FROM Author WHERE id = {author_id}")
        db.commit()
        cursor.execute(f"DELETE FROM ItemAuthor WHERE AuthorId = {author_id}")
        db.commit()
        logger.info(f"Author {author} removed.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error removing author {author}: {e}")
        return False


def get_item_authors(db: sqlite3.Connection, item_id: int, logger) -> list:
    '''Get the authors of an item from the database.'''
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT AuthorId FROM ItemAuthor WHERE ItemId = {item_id}")
        authors = cursor.fetchall()
        authorsdata = []
        for i in range(len(authors)):
            authorsdata.append(authors[i][0])

        logger.info(f"Got authors for item {item_id}: {authorsdata}")
        return authorsdata
    except sqlite3.Error as e:
        logger.error(f"Error getting authors for item {item_id}: {e}")
