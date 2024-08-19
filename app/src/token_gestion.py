import sqlite3
from datetime import datetime
import random
from enum import Enum

import db_gestion
import logging

class Permission:
    def __init__(self, string: str = None):
        self.create_content = 0
        self.remove_content = 0
        self.edit_content = 0
        self.search_content = 0

        self.create_tag = 0
        self.remove_tag = 0
        self.edit_tag = 0

        self.create_album = 0
        self.remove_album = 0
        self.dissolve_album = 0
        self.edit_album_content = 0
        self.edit_album_tags = 0
        self.search_album = 0

        self.add_author = 0
        self.delete_author = 0
        self.edit_author = 0
        self.search_author = 0

        self.is_admin = 0

        if string is not None:
            self.decode(string)

    def encode(self):
        content_slot = 0b1000 * self.create_content + 0b0100 * self.remove_content + 0b0010 * self.edit_content + 0b0001 * self.search_content
        tag_slot = 0b0100 * self.create_tag + 0b0010 * self.remove_tag + 0b0001 * self.edit_tag
        album_slot_1 = 0b0010 * self.create_album + 0b0001 * self.remove_album
        album_slot_2 = 0b1000 * self.dissolve_album + 0b0100 * self.edit_album_content + 0b0010 * self.edit_album_tags + 0b0001 * self.search_album
        author_slot = 0b1000 * self.add_author + 0b0100 * self.delete_author + 0b0010 * self.edit_author + 0b0001 * self.search_author
        admin_slot = 0b0001 * self.is_admin

        hex_content = hex(content_slot)[2:]
        hex_tag = hex(tag_slot)[2:]
        hex_album_1 = hex(album_slot_1)[2:]
        hex_album_2 = hex(album_slot_2)[2:]
        hex_author = hex(author_slot)[2:]
        hex_admin = hex(admin_slot)[2:]

        return hex_content + hex_tag + hex_album_1 + hex_album_2 + hex_author + hex_admin

    def decode(self, string: str):
        content_slot = int(string[0], 16)
        tag_slot = int(string[1], 16)
        album_slot_1 = int(string[2], 16)
        album_slot_2 = int(string[3], 16)
        author_slot = int(string[4], 16)
        admin_slot = int(string[5], 16)

        self.create_content = 1 if (content_slot & 0b1000) != 0 else 0
        self.remove_content = 1 if (content_slot & 0b0100) != 0 else 0
        self.edit_content = 1 if (content_slot & 0b0010) != 0 else 0
        self.search_content = 1 if (content_slot & 0b0001) != 0 else 0

        self.create_tag = 1 if (tag_slot & 0b0100) != 0 else 0
        self.remove_tag = 1 if (tag_slot & 0b0010) != 0 else 0
        self.edit_tag = 1 if (tag_slot & 0b0001) != 0 else 0

        self.create_album = 1 if (album_slot_1 & 0b0010) != 0 else 0
        self.remove_album = 1 if (album_slot_1 & 0b0001) != 0 else 0
        self.dissolve_album = 1 if (album_slot_2 & 0b1000) != 0 else 0
        self.edit_album_content = 1 if (album_slot_2 & 0b0100) != 0 else 0
        self.edit_album_tags = 1 if (album_slot_2 & 0b0010) != 0 else 0
        self.search_album = 1 if (album_slot_2 & 0b0001) != 0 else 0

        self.add_author = 1 if (author_slot & 0b1000) != 0 else 0
        self.delete_author = 1 if (author_slot & 0b0100) != 0 else 0
        self.edit_author = 1 if (author_slot & 0b0010) != 0 else 0
        self.search_author = 1 if (author_slot & 0b0001) != 0 else 0

        self.is_admin = 1 if (admin_slot & 0b0001) != 0 else 0

        return self

    def dictionnary(self):
        return {
            "create_content": True if self.create_content == 1 else False,
            "remove_content": True if self.remove_content == 1 else False,
            "edit_content": True if self.edit_content == 1 else False,
            "search_content": True if self.search_content == 1 else False,
            "create_tag": True if self.create_tag == 1 else False,
            "remove_tag": True if self.remove_tag == 1 else False,
            "edit_tag": True if self.edit_tag == 1 else False,
            "create_album": True if self.create_album == 1 else False,
            "remove_album": True if self.remove_album == 1 else False,
            "dissolve_album": True if self.dissolve_album == 1 else False,
            "edit_album_content": True if self.edit_album_content == 1 else False,
            "edit_album_tags": True if self.edit_album_tags == 1 else False,
            "search_album": True if self.search_album == 1 else False,
            "add_author": True if self.add_author == 1 else False,
            "delete_author": True if self.delete_author == 1 else False,
            "edit_author": True if self.edit_author == 1 else False,
            "search_author": True if self.search_author == 1 else False,
            "is_admin": True if self.is_admin == 1 else False
        }

class Permissions(Enum):
    CREATE_CONTENT = 0
    REMOVE_CONTENT = 1
    EDIT_CONTENT = 2
    SEARCH_CONTENT = 3
    CREATE_TAG = 4
    REMOVE_TAG = 5
    EDIT_TAG = 6
    CREATE_ALBUM = 7
    REMOVE_ALBUM = 8
    DISSOLVE_ALBUM = 9
    EDIT_ALBUM_CONTENT = 10
    EDIT_ALBUM_TAGS = 11
    SEARCH_ALBUM = 12
    ADD_AUTHOR = 13
    DELETE_AUTHOR = 14
    EDIT_AUTHOR = 15
    SEARCH_AUTHOR = 16
    IS_ADMIN = 17

class User:
    def __init__(self):
        self.id = None
        self.username = None
        self.token = None
        self.created_at = None
        self.last_usage = None
        self.is_active = None
        self.permissions = Permission()


def generate_token(username: str):
    seed = str(random.randint(0, 1000000)) + str(int(datetime.now().timestamp()))
    token = ""
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(0, 150):
        token += chars[random.randint(0, len(chars) - 1)]
    token += seed
    return token


def check_users_tables(db: sqlite3.Connection, logger):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        create_users_tables(db, logger)


def create_users_tables(db: sqlite3.Connection, logger):
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, token TEXT, created_at TEXT, last_usage TEXT, is_active INTEGER, permissions TEXT)")


def save_token(db: sqlite3.Connection, username: str, token: str) -> int or None:
    if get_token_info(db, token) is not None:
        return None
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, token) VALUES (?, ?)", (username, token))
    db.commit()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    return cursor.fetchone()[0]


def set_token_permissions(db: sqlite3.Connection, token: str, permissions: Permission) -> None:
    cursor = db.cursor()
    cursor.execute("UPDATE users SET permissions = ? WHERE token = ?", (permissions.encode(), token))
    db.commit()


def get_token_info(db: sqlite3.Connection, token: str) -> User or None:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE token = ?", (token,))
    data = cursor.fetchone()
    if data is None:
        return None
    user = User()
    user.id = data[0]
    user.username = data[1]
    user.token = data[2]
    user.created_at = data[3]
    user.last_usage = data[4]
    user.is_active = data[5]
    user.permissions.decode(data[6])
    return user


def get_user(db: sqlite3.Connection, username: str) -> User or None:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    data = cursor.fetchone()
    print(data)
    if data is None:
        return None
    user = User()
    user.id = data[0]
    user.username = data[1]
    user.token = data[2]
    user.created_at = data[3]
    user.last_usage = data[4]
    user.is_active = data[5]
    if data[6] is not None:
        user.permissions.decode(data[6])
    return user


def create_user(db: sqlite3.Connection, username: str, permissions: Permission, logger) -> User or None:
    if get_user(db, username) is not None:
        logger.error("User already exists")
        return None
    logger.info(f"Creating user {username} with permissions {permissions.encode()}")
    new_token = generate_token(username)
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, token, created_at, last_usage, is_active, permissions) VALUES (?, ?, ?, ?, ?, ?)", (username, new_token, datetime.now(), None, 1, permissions.encode()))
    db.commit()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))

    logger.info(f"User {username} created successfully")

    return {"id": cursor.fetchone()[0], "username": username, "token": new_token, "permissions": permissions.encode()}

def remove_user(db: sqlite3.Connection, username: str) -> None:
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    db.commit()

def check_token_permission(db: sqlite3.Connection, token: str, permission: Permissions = None) -> bool:
    user = get_token_info(db, token)
    if user is None or not user.is_active:
        return False
    if permission is None or user.permissions.dictionnary()[permission.name.lower()]:
        return True
    return False


# Defined permissions for now
# defined as a list of characters in hex
#####################
# create_content
# remove_content
# edit_content
# search_content
#
# #
# create_tag
# remove_tag
# edit_tag
#
# #
# #
# create_album
# remove_album
# dissolve_album
# edit_album_content
# edit_album_tags
# search_album
#
# add_author
# delete_author
# edit_author
# search_author
#
# #
# #
# #
# is_admin
#####################
