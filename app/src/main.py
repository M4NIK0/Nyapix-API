import hashlib
import os
from fastapi import Header
import fastapi
import uvicorn
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import db_gestion, token_gestion
import random
from pydantic import BaseModel
from typing import List, Generator, Annotated
from starlette.responses import StreamingResponse
import re
import cv2
import asyncio
import time
from fastapi import Depends
from logging.config import dictConfig

from token_gestion import check_token_permission, Permissions


############################################################################################################
# Models & data manipulation
#
# These models are used to define the data that is sent to and from the API.
# The data manipulation functions are used to generate names, calculate hashes and create thumbnails.
############################################################################################################

class CreateDb(BaseModel):
    api_key: str


class CreateUser(BaseModel):
    api_key: str
    username: str
    permissions: str


class RemoveUser(BaseModel):
    api_key: str
    username: str


class Item(BaseModel):
    api_key: str
    name: str
    tags: List[str]
    extension: str


class TagEdit(BaseModel):
    api_key: str
    tag: str
    new_tag: str


class Tag(BaseModel):
    api_key: str
    tag: str


class TagList(BaseModel):
    api_key: str


class Search(BaseModel):
    api_key: str
    tags: List[str]
    authors: List[str]
    sources: List[str]


class Author(BaseModel):
    api_key: str
    author: str


class AuthorEdit(BaseModel):
    api_key: str
    author: str
    new_author: str


class AddItem(BaseModel):
    api_key: str
    tags: List[str]
    authors: List[str]
    name: str
    filetype: str


class SearchTags(BaseModel):
    api_key: str
    tags: List[str]


class EditItem(BaseModel):
    api_key: str
    id: int
    tags: List[str]
    name: str
    authors: List[str]


class ItemId(BaseModel):
    api_key: str
    id: int


class GenericResponse(BaseModel):
    success: bool
    error: str = None
    data: dict = None


app = fastapi.FastAPI(debug=True) # API client instance

def calculate_file_sha256(file):
    file_hash = hashlib.sha256()
    while chunk := file.read(8192):
        file_hash.update(chunk)
    return file_hash.hexdigest()


def create_thumbnail(video_path: str, thumbnail_path: str):
    '''create 480p thumbnail from video_path and save it to thumbnail_path'''
    fmt = get_html_type_from_extension(video_path.split(".")[-1])
    if "video" in fmt:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2)
        ret, frame = cap.read()
        file_ratio = frame.shape[1] / frame.shape[0]
        frame = cv2.resize(frame, (480, int(480 / file_ratio)))
        if ret:
            cv2.imwrite(thumbnail_path, frame)
        cap.release()

    if "image" in fmt:
        if "gif" in fmt:
            img = cv2.VideoCapture(video_path)
            ret, frame = img.read()
            file_ratio = frame.shape[1] / frame.shape[0]
            frame = cv2.resize(frame, (480, int(480 / file_ratio)))
            cv2.imwrite(thumbnail_path, frame)
        else:
            img = cv2.imread(video_path)
            file_ratio = img.shape[1] / img.shape[0]
            img = cv2.resize(img, (480, int(480 / file_ratio)))
            cv2.imwrite(thumbnail_path, img)


def get_random_name():
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for i in range(20))


def get_html_type_from_extension(extension: str):
    vid_extensions = ["mp4", "webm", "mkv", "avi", "mov", "flv", "wmv", "3gp", "3g2", "m4v", "mpg", "mpeg", "m2v", "m4v", "f4v", "f4p", "f4a", "f4b"]
    img_extensions = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "tiff"]
    if extension in vid_extensions:
        return "video/" + extension
    elif extension in img_extensions:
        return "image/" + extension
    else:
        return None


def get_chunk(file_path: str, start: int, end: int) -> Generator[bytes, None, None]:
    with open(file_path, "rb") as f:
        f.seek(start)
        while start < end:
            chunk_size = min(1024 * 1024, end - start)
            data = f.read(chunk_size)
            if not data:
                break
            start += len(data)
            yield data


def get_content_size():
    total_size = 0

    for dirpath, dirnames, filenames in os.walk("data/nyapix-content/content"):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size



############################################################################################################
# Configuration
#
# Load the configuration from the .env file.
############################################################################################################

load_dotenv()

master_key = os.getenv("MASTER_KEY")
if master_key is None:
    raise Exception("No master key found in .env file.")

port = int(os.getenv("PORT"))
if port is None:
    raise Exception("No port found in .env file.")

bg_task = None



############################################################################################################
# Background tasks
#
# For now, the only background task is the statistics task.
###########################################################################################################

async def stats_task():
    """Get statistics every day and write them to a CSV file."""
    while True:
        logger.info("Starting statistics task")
        db = db_gestion.connect_db("nyapix_content.db", logger)
        if db is not None:
            stats = db_gestion.get_tags_statistics(db, logger)
            db.close()

            if not os.path.exists("data/nyapix-content"):
                os.makedirs("data/nyapix-content")
            if not os.path.exists("data/nyapix-content/stats.csv"):
                with open("data/nyapix-content/stats.csv", "w") as f:
                    f.write("timestamp,total_items,total_tags,total_used_tags,total_unused_tags,top_tags,total_size\n")

            if stats["success"]:
                total_items_count = stats["images"]

                total_tags_count = stats["tags"]["total"]
                used_taglist = stats["tags"]["used"]
                unused_taglist = stats["tags"]["unused"]
                total_unused_tags_count = len(unused_taglist)
                total_used_tags_count = len(used_taglist)

                sorted_used_tags = sorted(used_taglist, key=lambda x: x['count'], reverse=True)[:20]

                total_size = get_content_size()

                logger.info(f"Total items: {total_items_count}")
                logger.info(f"Total tags: {total_tags_count}")
                logger.info(f"Total used tags: {total_used_tags_count}")
                logger.info(f"Total unused tags: {total_unused_tags_count}")
                logger.info(f"Total content size: {total_size} bytes")

                csv_line = ""
                timestamp = int(time.time())

                csv_line += str(timestamp) + ","
                csv_line += str(total_items_count) + ","
                csv_line += str(total_tags_count) + ","
                csv_line += str(total_used_tags_count) + ","
                csv_line += str(total_unused_tags_count) + ","
                for tag in sorted_used_tags:
                    csv_line += tag["name"] + "," + str(tag["count"]) + ","
                csv_line += str(total_size)
                csv_line += "\n"

                with open("data/nyapix-content/stats.csv", "a") as f:
                    f.write(csv_line)

        # Add a delay for the loop to wait until the next statistics update
        await asyncio.sleep(86400)


@app.on_event("startup")
async def startup_event():
    global bg_task
    bg_task = asyncio.create_task(stats_task())
    print("Background task started.")


@app.on_event("shutdown")
async def shutdown_event():
    global bg_task
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        print("Background task cancelled on shutdown.")
    print("Background task stopped.")



############################################################################################################
# Technical endpoints
#
# The technical endpoints are used to get information about the server.
#
# nyapix_version - Get the version of the Nyapix server
# ping - Ping the server and check if api key is valid
# createdb - Create the database tables (admin only)
############################################################################################################

@app.get("/nyapix_version")
async def nyapix_version():
    return {"version": "0.1"}


def get_create_db_headers(api_key: str = Header(...)) -> CreateDb:
    return CreateDb(api_key=api_key)


@app.get("/ping")
async def ping(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info("Got a request to /ping")

    user_db = db_gestion.connect_db("nyapix_users.db", logger)
    if user_db is not None:
        has_permission = check_token_permission(user_db, logger, headers.api_key, None)
        user_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}

    return {"success": True}


@app.get("/admin/setup")
async def create_db(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info("Got a request to /createdb")

    if headers.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}

    content_db = db_gestion.connect_db("nyapix_content.db", logger)
    if content_db is not None and not db_gestion.check_content_tables(content_db, logger):
        db_gestion.create_content_tables(content_db, logger)
    content_db.close()

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None and not token_gestion.check_users_tables(users_db, logger):
        token_gestion.create_users_tables(users_db, logger)
    users_db.close()

    return {"success": True}




############################################################################################################
# Tags management endpoints
#
# The tags management endpoints are used to manage the tags in the database.
#
# addtag - Add a tag to the database
# removetag - Remove a tag from the database
# edittag - Edit a tag in the database
# taglist - Get a list of all tags in the database
############################################################################################################

def post_add_tag(api_key: str = Header(...), tag: str = Header(...)) -> Tag:
    return Tag(api_key=api_key, tag=tag)

@app.post("/tag/add")
async def addtag(headers: Tag = Depends(post_add_tag)):
    logger.info(f"Got a request to /addtag")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.CREATE_TAG)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        db_gestion.add_tag(db, headers.tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/tag/remove")
async def removetag(headers: Tag = Depends(post_add_tag)):
    logger.info(f"Got a request to /removetag")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.REMOVE_TAG)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        db_gestion.remove_tag(db, headers.tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


def post_edit_tag(api_key: str = Header(...), tag: str = Header(...), new_tag: str = Header(...)) -> TagEdit:
    return TagEdit(api_key=api_key, tag=tag, new_tag=new_tag)


@app.post("/tag/edit")
async def edittag(headers: TagEdit = Depends(post_edit_tag)):
    logger.info(f"Got a request to /tagedit")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.EDIT_TAG)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        tag_id = db_gestion.get_tag_id(db, headers.tag, logger)
        if tag_id is None:
            return {"success": False, "error": "Tag not found."}
        db_gestion.edit_tag(db, tag_id, headers.new_tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/tag/list")
async def taglist(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info(f"Got a request to /taglist")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.SEARCH_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        taglistfinal = db_gestion.get_taglist(db, logger)
        db.close()
        return {"tags": taglistfinal, "success": True}
    else:
        return {"success": False, "error": "Database error."}



############################################################################################################
# Author management endpoints
#
# The author management endpoints are used to manage the authors in the database.
#
# addauthor - Add an author to the database
# removeauthor - Remove an author from the database
# editauthor - Edit an author in the database
# authorlist - Get a list of all authors in the database
############################################################################################################

@app.get("/author/list")
async def authorlist(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info(f"Got a request to /authorlist")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.SEARCH_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        authorlistfinal = db_gestion.get_authorslist(db, logger)
        db.close()
        return {"authors": authorlistfinal, "success": True}
    else:
        return {"success": False, "error": "Database error."}

def post_add_author(api_key: str = Header(...), author: str = Header(...)) -> Author:
    return Author(api_key=api_key, author=author)


@app.post("/author/create")
async def addauthor(headers: Author = Depends(post_add_author)):
    logger.info(f"Got a request to /addauthor")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.ADD_AUTHOR)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        db_gestion.add_author(db, headers.author, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


def post_remove_author(api_key: str = Header(...), author: str = Header(...)) -> Author:
    return Author(api_key=api_key, author=author)


@app.post("/author/remove")
async def removeauthor(headers: Author = Depends(post_remove_author)):
    logger.info(f"Got a request to /removeauthor")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.DELETE_AUTHOR)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        db_gestion.remove_author(db, headers.author, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


def post_edit_author(api_key: str = Header(...), author: str = Header(...), new_author: str = Header(...)) -> AuthorEdit:
    return AuthorEdit(api_key=api_key, author=author, new_author=new_author)


@app.post("/author/edit")
async def editauthor(headers: AuthorEdit = Depends(post_edit_author)):
    logger.info(f"Got a request to /editauthor")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.EDIT_AUTHOR)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        author_id = db_gestion.get_author_id(db, headers.author, logger)
        if author_id is None:
            return {"success": False, "error": "Author not found."}
        db_gestion.edit_author(db, author_id, headers.new_author, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


############################################################################################################
# Content management endpoints
#
# The content management endpoints are used to manage the content in the database.
#
# additem - Add an item to the database
# getitem - Get an item from the database
# removeitem - Remove an item from the database
# search - Search for items in the database
# edititem - Edit an item in the database
# stream_content - Stream content from the server (only for video files and from the content folder)
# get_content - Get content from the server (only for video files and from the content folder)
# get_thumb - Get the thumbnail of an item from the server
# download_content - Download content from the server
# purge_non_existing - Purge non-existing files from the database
############################################################################################################

def post_additem(api_key: str = Header(...), name: str = Header(...), tags: List[str] = Header(...), authors: List[str] = Header(...), filetype: str = Header(...)) -> AddItem:
    return AddItem(api_key=api_key, name=name, tags=tags[0].split(","), authors=authors[0].split(","), filetype=filetype)


@app.post("/item/add")
async def additem(headers: AddItem = Depends(post_additem), file: fastapi.UploadFile = fastapi.File(...)):
    logger.info(f"Got a request to /additem")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.CREATE_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}


    # Ensure the directory exists
    os.makedirs("data/nyapix-content/content", exist_ok=True)
    os.makedirs("data/nyapix-content/thumbs", exist_ok=True)

    if not os.path.exists("data/nyapix-content/tmp"):
        os.makedirs("data/nyapix-content/tmp")

    tmp_filename = get_random_name()

    file_contents = await file.read()
    with open(f"data/nyapix-content/tmp/{tmp_filename}", "wb") as f:
        f.write(file_contents)

    with open(f"data/nyapix-content/tmp/{tmp_filename}", "rb") as tmpfile:
        filename = calculate_file_sha256(tmpfile)

    filepath = f"data/nyapix-content/content/{filename}.{headers.filetype}"
    thumbpath = f"data/nyapix-content/thumbs/{filename}.png"

    if os.path.exists(filepath):
        os.remove(f"data/nyapix-content/tmp/{tmp_filename}")
        return {"success": False, "error": "Content already on server"}

    tags = [tag.strip() for tag in headers.tags]
    newitem = {"tags": tags, "name": headers.name, "type": headers.filetype, "path": filepath, "authors": headers.authors}
    if get_html_type_from_extension(headers.filetype) is None:
        os.remove(f"data/nyapix-content/tmp/{tmp_filename}")
        return {"success": False, "error": "Unsupported file type."}

    db = db_gestion.connect_db("nyapix_content.db", logger)

    if db is not None:
        result = db_gestion.add_item(db, {"name": newitem["name"], "path": newitem["path"], "tags": newitem["tags"], "authors": newitem["authors"]}, logger)
        if result["success"]:
            os.rename(f"data/nyapix-content/tmp/{tmp_filename}", filepath)
            create_thumbnail(filepath, thumbpath)
        else:
            os.remove(f"data/nyapix-content/tmp/{tmp_filename}")
        db.close()
        return result
    else:
        return {"success": False, "error": "Database error."}


def get_getitem(api_key: str = Header(...), id: int = Header(...)) -> ItemId:
    return ItemId(api_key=api_key, id=id)


@app.post("/item/remove")
async def removeitem(headers: ItemId = Depends(get_getitem)):
    logger.info(f"Got a request to /removeitem")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.REMOVE_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)

    if db is not None:
        # remove file
        item = db_gestion.get_item(db, headers.id, logger)
        if item is None:
            db.close()
            return {"success": False, "error": "Item not found."}
        thumbnail_location = "data/nyapix-content/thumbs/" + item["path"].split("/")[-1].split(".")[0] + ".png"
        if os.path.isfile(item["path"]):
            os.remove(item["path"])
        if os.path.isfile(thumbnail_location):
            os.remove(thumbnail_location)
        logger.info(f"thumbnail location: {thumbnail_location}")
        success = db_gestion.remove_item(db, headers.id, logger)
        db.close()
        return {"success": success}
    else:
        return {"success": False, "error": "Database error."}


def get_search(
        api_key: str = Header(...),
        tags: List[str] = Header(None),
        authors: List[str] = Header(None),
        sources: List[str] = Header(None)
) -> Search:
    taglist = tags[0].split(",") if tags else []
    authorlist = authors[0].split(",") if authors else []
    sourceslist = sources[0].split(",") if sources else []
    return Search(api_key=api_key, tags=taglist, authors=authorlist, sources=sourceslist)


def post_edititem(api_key: str = Header(...), id: int = Header(...), name: str = Header(...), tags: List[str] = Header(...), authors: List[str] = Header(...)):
    return EditItem(api_key=api_key, id=id, name=name, tags=tags[0].split(","), authors=authors[0].split(","))


@app.post("/item/edit")
async def edititem(headers: EditItem = Depends(post_edititem)):
    logger.info(f"Got a request to /edititem")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.EDIT_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        item = db_gestion.get_item(db, headers.id, logger)
        if item is None:
            db.close()
            return {"success": False, "error": "Item not found."}
        logger.info(str(headers.tags) + " " + str(headers.authors))
        success_edit = db_gestion.edititem(db, headers.id, headers.name, headers.tags, headers.authors, logger)
        db.close()
        return {"success": success_edit}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/item/purge_nofile")
def purge_non_existing(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info(f"Got a request to /purge_non_existing")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        db_gestion.purge_non_existing(db, logger)
        db.close()
        return {"success": True}
    else:
        db.close()
        return {"success": False, "error": "Database error."}


@app.get("/content/search")
async def searchbytags(headers: Search = Depends(get_search)):
    logger.info(f"Got a request to /search")

    if len(headers.tags) is 0 and len(headers.authors) is 0 and len(headers.sources) is 0:
        resp = fastapi.Response(status_code=422)
        resp.body = {"success": False, "error": "No tags or authors provided."} # TODO: Return an error on wrong request

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.SEARCH_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        for tag in headers.tags:
            if db_gestion.get_tag_id(db, tag, logger) is None:
                db.close()
                return {"success": False, "error": "Tag not found."}

        items = db_gestion.get_items_with_tags(db, headers.tags, logger)
        result = [{"id": item["id"], "name": item["name"], "tags": item["tags"]} for item in items]
        db.close()
        return {"success": True, "result": result}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/content/{content_id}/info")
async def getitem(content_id: int, headers: CreateDb = Depends(get_create_db_headers)):
    '''
    :param data: {"api_key": str, "id": int}
    :return:
    '''
    logger.info(f"Got a request to /getitem")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.SEARCH_CONTENT)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        item = db_gestion.get_item(db, content_id, logger)
        db.close()
        if item is None:
            return {"success": False, "error": "Item not found."}
        return {"success": True, "item": {"id": item["id"], "type": item["extension"], "size": item["size"], "name": item["name"], "tags": item["tags"], "authors": item["authors"]}}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/content/{content_id}/stream")
async def stream_content(content_id: int, request: fastapi.Request):
    logger.info(f"Got a request to stream /content/{content_id}/stream")
    db = db_gestion.connect_db("nyapix_content.db", logger)
    path = db_gestion.get_item(db, content_id, logger)

    if path is None or not os.path.isfile(path["path"]):
        db.close()
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    file_path = path["path"]
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range", None)

    if not range_header:
        db.close()
        return StreamingResponse(
            get_chunk(file_path, 0, file_size),
            media_type="video/mp4"
        )

    range_match = re.match(r"bytes=(\d+)-(\d+)?", range_header)
    if range_match:
        start = int(range_match.group(1))
        end = range_match.group(2)
        end = int(end) if end else file_size - 1
    else:
        db.close()
        raise fastapi.HTTPException(status_code=400, detail="Invalid range header")

    if start >= file_size or end >= file_size:
        db.close()
        raise fastapi.HTTPException(status_code=416, detail="Requested range not satisfiable")

    db.close()
    return StreamingResponse(
        get_chunk(file_path, start, end + 1),
        media_type="video/mp4",
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
        },
        status_code=206
    )


@app.get("/content/{content_id}")
def get_content(content_id: int):
    logger.info(f"Got a request to /content/{content_id}")
    db = db_gestion.connect_db("nyapix_content.db", logger)
    path = db_gestion.get_item(db, content_id, logger)

    if path is None or "path" not in path.keys() or not os.path.isfile(path["path"]):
        logger.error(f"File not found for content or content not found in database.")
        with open("data/nyapix-content/error.png", "r") as file:
            db.close()
            return fastapi.responses.FileResponse("data/nyapix-content/error.png", media_type="image/png")

    fmt = get_html_type_from_extension(path["path"].split(".")[-1])
    if "image" in fmt:
        db.close()
        return fastapi.responses.FileResponse(path["path"], media_type=fmt)

    response = fastapi.responses.HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>Video {content_id}</title>
            </head>
            <body>
                <video width="640" height="360" controls>
                    <source src="/content/{content_id}/stream" type="{fmt}">
                    Your browser does not support the video tag.
                </video>
            </body>
        </html>
        """,
        status_code=200
    )

    db.close()
    return response


@app.get("/content/{content_id}/thumb")
def get_thumb(content_id: int):
    logger.info(f"Got a request to /content/{content_id}/thumb")
    db = db_gestion.connect_db("nyapix_content.db", logger)
    path = db_gestion.get_item(db, content_id, logger)

    if path is None:
        db.close()
        return fastapi.responses.FileResponse("data/nyapix-content/error.png", media_type="image/png")

    thumb_name = path["path"].split("/")[-1].split(".")[0]
    thumb_path = "data/nyapix-content/thumbs/" + thumb_name + ".png"

    if not os.path.isfile(thumb_path):
        db.close()
        return fastapi.responses.FileResponse("data/nyapix-content/error.png", media_type="image/png", status_code=404)

    db.close()
    return fastapi.responses.FileResponse(thumb_path, media_type="image/png")


@app.get("/content/{content_id}/download")
def download_content(content_id: int):
    logger.info(f"Got a request to /content/{content_id}/download")
    db = db_gestion.connect_db("nyapix_content.db", logger)
    path = db_gestion.get_item(db, content_id, logger)

    if path is None or "path" not in path.keys() or not os.path.isfile(path["path"]):
        db.close()
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    db.close()
    return fastapi.responses.FileResponse(path["path"])



############################################################################################################
# Album management endpoints
#
# The album management endpoints are used to manage the albums in the database.
#
# album_creation - Create an album # TODO : add this endpoint
# - from archive # TODO : add this endpoint
# - from content IDs # TODO : add this endpoint
# album_deletion - Delete an album # TODO : add this endpoint
# - delete album and content from database # TODO : add this endpoint
# - dissolve album and keep content in database (apply album tags and album name to content) # TODO : add this endpoint
# album_edit - Edit an album # TODO : add this endpoint
# - edit album name and tags # TODO : add this endpoint
# - remove content from album # TODO : add this endpoint
# - add content to album # TODO : add this endpoint
# album_search - Search for albums # TODO : add this endpoint
# album_get - Get an album # TODO : add this endpoint
############################################################################################################



############################################################################################################
# Statistics endpoints
#
# The statistics endpoints are used to get statistics about the content in the database.
#
# statistics - Get statistics for the current day
# statistics_csv - Get statistics for all time in CSV format
############################################################################################################

@app.get("/statistics/current")
def statistics(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info(f"Got a request to /statistics")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    db = db_gestion.connect_db("nyapix_content.db", logger)
    if db is not None:
        stats = db_gestion.get_tags_statistics(db, logger)
        db.close()
        return stats
    else:
        return {"success": False, "error": "Database error."}


@app.get("/statistics/all-time")
def statistics_csv(headers: CreateDb = Depends(get_create_db_headers)):
    logger.info(f"Got a request to /statistics/csv")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return {"success": False, "error": "Invalid API key."}
    else:
        return {"success": False, "error": "User database error."}

    if not os.path.exists("data/nyapix-content/stats.csv"):
        return {"success": False, "error": "No statistics available."}
    with open("data/nyapix-content/stats.csv", "r") as f:
        return f.read()



############################################################################################################
# User management endpoints (admin only)
#
# The user management endpoints are used to manage the users of the API.
#
# adduser - Add a user to the database
# removeuser - Remove a user from the database
# getuser - Get a user from the database
# edituser - Set the permissions of a user
############################################################################################################

def get_create_user(api_key: str = Header(...), username: str = Header(...), permissions: str = Header(...)) -> CreateUser:
    return CreateUser(api_key=api_key, username=username, permissions=permissions)


@app.post("/user/add")
def add_user(headers: CreateUser = Depends(get_create_user)) -> GenericResponse:
    logger.info(f"Got a request to /user/add")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return GenericResponse(success=False, error="Invalid API key.")
    else:
        return GenericResponse(success=False, error="User database error.")

    db = db_gestion.connect_db("nyapix_users.db", logger)
    if db is not None:
        user = token_gestion.create_user(db, headers.username, token_gestion.Permission(headers.permissions), logger)
        if user is None:
            db.close()
            return GenericResponse(success=False, error="User already exists.")
        db.close()
        return GenericResponse(success=True, data = user)
    return GenericResponse(success=False, error="Database error.")


def get_remove_user(api_key: str = Header(...), username: str = Header(...)) -> RemoveUser:
    return RemoveUser(api_key=api_key, username=username)


@app.post("/user/remove")
def remove_user(headers: RemoveUser = Depends(get_remove_user)) -> GenericResponse:
    logger.info(f"Got a request to /user/remove")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return GenericResponse(success=False, error="Invalid API key.")
    else:
        return GenericResponse(success=False, error="User database error.")

    db = db_gestion.connect_db("nyapix_users.db", logger)
    if db is not None:
        token_gestion.remove_user(db, headers.username)
        db.close()
        return GenericResponse(success=True)
    return GenericResponse(success=False, error="Database error.")


@app.get("/user/info")
def get_user(headers: RemoveUser = Depends(get_remove_user)) -> GenericResponse:
    logger.info(f"Got a request to /user/info")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return GenericResponse(success=False, error="Invalid API key.")
    else:
        return GenericResponse(success=False, error="User database error.")

    db = db_gestion.connect_db("nyapix_users.db", logger)
    if db is not None:
        user = token_gestion.get_user(db, headers.username)
        if user is None:
            db.close()
            return GenericResponse(success=False, error="User does not exist.")
        db.close()
        return GenericResponse(success=True, data={"username": user.username, "permissions": user.permissions.dictionnary(), "is_active": user.is_active})
    return GenericResponse(success=False, error="Database error.")


@app.post("/user/edit")
def edit_user(headers: CreateUser = Depends(get_create_user)) -> GenericResponse:
    logger.info(f"Got a request to /user/edit")

    users_db = db_gestion.connect_db("nyapix_users.db", logger)
    if users_db is not None:
        has_permission = check_token_permission(users_db, logger, headers.api_key, Permissions.IS_ADMIN)
        users_db.close()
        if not has_permission and headers.api_key != master_key:
            return GenericResponse(success=False, error="Invalid API key.")
    else:
        return GenericResponse(success=False, error="User database error.")

    db = db_gestion.connect_db("nyapix_users.db", logger)
    if db is not None:
        user = get_user(db, headers.username)
        if user is None:
            db.close()
            return GenericResponse(success=False, error="User does not exist.")
        new_permissions = token_gestion.Permission(headers.permissions)
        token_gestion.set_token_permissions(db, user.token, new_permissions)
        db.close()
        return GenericResponse(success=True)
    return GenericResponse(success=False, error="Database error.")



############################################################################################################
# Client management endpoints
#
# The client management endpoints are used to manage the clients of the API.
#
# version - Get the version of the Nyapix client # TODO : add this endpoint
# download - Download the Nyapix client # TODO : add this endpoint
############################################################################################################



############################################################################################################
# Config
#
# Configuration of the API server and run the server.
#
# logger - The main logger of the server
# fastapi client - The FastAPI client
# run - Run the server
############################################################################################################

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "main_logger": {"handlers": ["default"], "level": "DEBUG"},
    },
}

dictConfig(log_config)

logger = logging.getLogger("main_logger")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler('logs/nyapix.log', maxBytes=1024*1024, backupCount=5)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
