import hashlib
import os
import fastapi
import uvicorn
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import db_gestion
import random
from pydantic import BaseModel
from typing import List, Generator
from starlette.responses import StreamingResponse
import re
import cv2
import asyncio
import time
from logging.config import dictConfig

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


class CreateDb(BaseModel):
    api_key: str


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


class AddItem(BaseModel):
    api_key: str
    tags: List[str]
    name: str
    type: str
    file: fastapi.UploadFile


class SearchTags(BaseModel):
    api_key: str
    tags: List[str]


class EditItem(BaseModel):
    api_key: str
    id: int
    tags: List[str]
    name: str


class ItemId(BaseModel):
    api_key: str
    id: int


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


load_dotenv()

master_key = os.getenv("MASTER_KEY")
if master_key is None:
    raise Exception("No master key found in .env file.")

port = int(os.getenv("PORT"))
if port is None:
    raise Exception("No port found in .env file.")

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

app = fastapi.FastAPI(debug=True)
bg_task = None


def get_content_size():
    total_size = 0

    for dirpath, dirnames, filenames in os.walk("data/nyapix-content/content"):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


async def stats_task():
    """Get statistics every day and write them to a CSV file."""
    while True:
        logger.info("Starting statistics task")
        db = db_gestion.connect_db("nyapic.db", logger)
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


@app.get("/nyapix_version")
async def nyapix_version():
    return {"version": "0.1"}


@app.get("/ping")
async def ping(data: TagList):
    logger.info("Got a request to /ping")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    return {"success": True}


@app.get("/createdb")
async def create_db(data: CreateDb):
    logger.info("Got a request to /createdb")
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None and not db_gestion.check_content_tables(db, logger):
        db_gestion.create_content_tables(db, logger)
        db.close()
    return {"success": True}


@app.post("/addtag")
async def addtag(tag: Tag):
    logger.info(f"Got a request to /addtag")
    if tag.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        db_gestion.add_tag(db, tag.tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/removetag")
async def removetag(tag: Tag):
    logger.info(f"Got a request to /removetag")
    if tag.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        db_gestion.remove_tag(db, tag.tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/edittag")
async def edittag(data: TagEdit):
    logger.info(f"Got a request to /tagedit")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        tag_id = db_gestion.get_tag_id(db, data.tag, logger)
        if tag_id is None:
            return {"success": False, "error": "Tag not found."}
        db_gestion.edit_tag(db, tag_id, data.new_tag, logger)
        db.close()
        return {"success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/taglist")
async def taglist(data: TagList):
    logger.info(f"Got a request to /taglist")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        taglistfinal = db_gestion.get_taglist(db, logger)
        db.close()
        return {"tags": taglistfinal, "success": True}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/additem")
async def additem(api_key: str, name: str, tags: List[str], filetype: str, file: fastapi.UploadFile = fastapi.File(...)):
    logger.info(f"Got a request to /additem")
    if api_key != master_key:
        return {"success": False, "error": "Invalid API key."}

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

    filepath = f"data/nyapix-content/content/{filename}.{filetype}"
    thumbpath = f"data/nyapix-content/thumbs/{filename}.png"

    if os.path.exists(filepath):
        os.remove(f"data/nyapix-content/tmp/{tmp_filename}")
        return {"success": False, "error": "Content already on server"}

    tags = [tag.strip() for tag in tags]
    newitem = {"tags": tags, "name": name, "type": filetype, "path": filepath}
    if get_html_type_from_extension(filetype) is None:
        return {"success": False, "error": "Unsupported file type."}

    db = db_gestion.connect_db("nyapic.db", logger)

    if db is not None:
        result = db_gestion.add_item(db, {"name": newitem["name"], "path": newitem["path"], "tags": newitem["tags"]}, logger)
        if result["success"]:
            os.rename(f"data/nyapix-content/tmp/{tmp_filename}", filepath)
            create_thumbnail(filepath, thumbpath)
        db.close()
        return result
    else:
        return {"success": False, "error": "Database error."}


@app.get("/getitem")
async def getitem(data: ItemId):
    '''
    :param data: {"api_key": str, "id": int}
    :return:
    '''
    logger.info(f"Got a request to /getitem")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        item = db_gestion.get_item(db, data.id, logger)
        db.close()
        if item is None:
            return {"success": False, "error": "Item not found."}
        return {"success": True, "item": {"id": item["id"], "type": item["extension"], "size": item["size"], "name": item["name"], "tags": item["tags"]}}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/removeitem")
async def removeitem(data: ItemId):
    logger.info(f"Got a request to /removeitem")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)

    if db is not None:
        # remove file
        item = db_gestion.get_item(db, data.id, logger)
        if item is None:
            db.close()
            return {"success": False, "error": "Item not found."}
        thumbnail_location = "data/nyapix_content/" + item["path"].split("/")[-1]
        if os.path.isfile(item["path"]):
            os.remove(item["path"])
        if os.path.isfile(thumbnail_location):
            os.remove(thumbnail_location)
        success = db_gestion.remove_item(db, data.id, logger)
        db.close()
        return {"success": success}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/search")
async def searchbytags(data: SearchTags):
    logger.info(f"Got a request to /search")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        for tag in data.tags:
            if db_gestion.get_tag_id(db, tag, logger) is None:
                db.close()
                return {"success": False, "error": "Tag not found."}

        items = db_gestion.get_items_with_tags(db, data.tags, logger)
        result = [{"id": item["id"], "name": item["name"], "tags": item["tags"]} for item in items]
        db.close()
        return {"success": True, "result": result}
    else:
        return {"success": False, "error": "Database error."}


@app.post("/edititem")
async def edititem(data: EditItem):
    logger.info(f"Got a request to /edititem")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        item = db_gestion.get_item(db, data.id, logger)
        if item is None:
            db.close()
            return {"success": False, "error": "Item not found."}
        success_edit = db_gestion.edititem(db, data.id, data.name, data.tags, logger)
        db.close()
        return {"success": success_edit}
    else:
        return {"success": False, "error": "Database error."}


@app.get("/content/{content_id}/stream")
async def stream_content(content_id: int, request: fastapi.Request):
    logger.info(f"Got a request to stream /content/{content_id}/stream")
    db = db_gestion.connect_db("nyapic.db", logger)
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
    db = db_gestion.connect_db("nyapic.db", logger)
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
    db = db_gestion.connect_db("nyapic.db", logger)
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


@app.post("/purge_non_existing")
def purge_non_existing(data: CreateDb):
    logger.info(f"Got a request to /purge_non_existing")
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        db_gestion.purge_non_existing(db, logger)
        db.close()
        return {"success": True}
    else:
        db.close()
        return {"success": False, "error": "Database error."}


@app.get("/statistics/current")
def statistics(data: TagList):
    logger.info(f"Got a request to /statistics")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    db = db_gestion.connect_db("nyapic.db", logger)
    if db is not None:
        stats = db_gestion.get_tags_statistics(db, logger)
        db.close()
        return stats
    else:
        return {"success": False, "error": "Database error."}


@app.get("/statistics/all-time")
def statistics_csv(data: TagList):
    logger.info(f"Got a request to /statistics/csv")
    if data.api_key != master_key:
        return {"success": False, "error": "Invalid API key."}
    if not os.path.exists("data/nyapix-content/stats.csv"):
        return {"success": False, "error": "No statistics available."}
    with open("data/nyapix-content/stats.csv", "r") as f:
        return f.read()


@app.get("/content/{content_id}/download")
def download_content(content_id: int):
    logger.info(f"Got a request to /content/{content_id}/download")
    db = db_gestion.connect_db("nyapic.db", logger)
    path = db_gestion.get_item(db, content_id, logger)

    if path is None or "path" not in path.keys() or not os.path.isfile(path["path"]):
        db.close()
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    db.close()
    return fastapi.responses.FileResponse(path["path"])

# TODO : add endpoints for client updates

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
