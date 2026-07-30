import json
import logging
from typing import Any

import requests

from src.models.contents import Content, ContentListModel, ContentPostModel

logger = logging.getLogger()


def get_my_contents(api_url: str, token: str, page: int, max_results: int = 10) -> ContentListModel | None:
    """
    Get authenticated user contents from server.
    :param api_url: API base URL
    :param token: Token
    :param page: Page number (starting from 1)
    :param max_results: Maximum results per page
    :return: ContentListModel or None
    """

    if api_url == "" or token == "" or page < 1 or max_results < 1:
        logger.error("API URL, token, page or max results is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/content/my?page={page}&max_results={max_results}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        contents = ContentListModel.model_validate(resp.json())
        logger.info("My contents retrieved successfully (Page " + str(page) + ")")
        return contents

    logger.error("My contents retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def search_contents(
        api_url: str,
        token: str,
        needed_tags: list[int] | None = None,
        needed_characters: list[int] | None = None,
        needed_authors: list[int] | None = None,
        tags_to_exclude: list[int] | None = None,
        characters_to_exclude: list[int] | None = None,
        authors_to_exclude: list[int] | None = None,
        page: int = 1,
        max_results: int = 10,
) -> ContentListModel | None:
    """
    Search contents on server.
    :param api_url: API base URL
    :param token: Token
    :param needed_tags: Needed tag IDs
    :param needed_characters: Needed character IDs
    :param needed_authors: Needed author IDs
    :param tags_to_exclude: Excluded tag IDs
    :param characters_to_exclude: Excluded character IDs
    :param authors_to_exclude: Excluded author IDs
    :param page: Page number
    :param max_results: Maximum results per page
    :return: ContentListModel or None
    """

    if api_url == "" or token == "" or page < 1 or max_results < 1:
        logger.error("API URL, token, page or max results is invalid")
        return None

    params: dict[str, Any] = {
        "page": page,
        "max_results": max_results,
    }

    if needed_tags:
        params["needed_tags"] = needed_tags
    if needed_characters:
        params["needed_characters"] = needed_characters
    if needed_authors:
        params["needed_authors"] = needed_authors
    if tags_to_exclude:
        params["tags_to_exclude"] = tags_to_exclude
    if characters_to_exclude:
        params["characters_to_exclude"] = characters_to_exclude
    if authors_to_exclude:
        params["authors_to_exclude"] = authors_to_exclude

    resp = requests.get(
        f"{api_url}/v1/content/search",
        params=params,
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        contents = ContentListModel.model_validate(resp.json())
        logger.info("Contents search succeeded (Page " + str(page) + ")")
        return contents

    logger.error("Contents search failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def get_content(api_url: str, token: str, content_id: int) -> Content | None:
    """
    Get content by ID.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :return: Content or None
    """

    if api_url == "" or token == "" or content_id < 1:
        logger.error("API URL, token or content ID is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/content/{content_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        content = Content.model_validate(resp.json())
        logger.info("Content retrieved successfully")
        return content

    logger.error("Content retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def get_content_owner(api_url: str, token: str, content_id: int) -> dict[str, Any] | None:
    """
    Get content owner.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :return: User payload or None
    """

    if api_url == "" or token == "" or content_id < 1:
        logger.error("API URL, token or content ID is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/content/{content_id}/who",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        logger.info("Content owner retrieved successfully")
        return resp.json()

    logger.error("Content owner retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None

def download_content(target_url: str, token: str, file_path: str) -> None:
    """
    Download content from a target URL.
    :param target_url: Target URL
    :param token: Token
    :param file_path: Path of the file to save, not including extension
    """

    if target_url == "" or token == "" or file_path == "":
        logger.error("Target URL, token or file name is invalid")
        return

    resp = requests.get(
        target_url,
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
    )

    if "image" in target_url:
        if not file_path.endswith(".png"):
            file_path += ".png"
    if "video" in target_url:
        if not file_path.endswith(".mp4"):
            file_path += ".mp4"
    if "audio" in target_url:
        if not file_path.endswith(".wav"):
            file_path += ".wav"

    if resp.status_code == 200:
        with open(file_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Content downloaded successfully to " + file_path)
    else:
        logger.error("Content download failed (Error " + str(resp.status_code) + ")")
        logger.warning(resp.text)

def download_thumb(api_url: str, token: str, content_id: int, file_path: str) -> None:
    """
    Download content thumb by ID.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :param file_path: Path of the file to save, not including extension
    """

    if api_url == "" or token == "" or content_id < 1 or file_path == "":
        logger.error("API URL, token, content ID or file name is invalid")
        return

    resp = requests.get(
        f"{api_url}/v1/content/{content_id}/thumb",
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
    )

    if not file_path.endswith(".png"):
        file_path += ".png"

    if resp.status_code == 200:
        with open(file_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("Content thumb downloaded successfully to " + file_path)
    else:
        logger.error("Content thumb download failed (Error " + str(resp.status_code) + ")")
        logger.warning(resp.text)

def update_content(api_url: str, token: str, content_id: int, content_update: dict[str, Any]) -> bool:
    """
    Update content by ID.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :param content_update: ContentUpdateModel payload as dict
    :return: True if update succeeded; False otherwise
    """

    if api_url == "" or token == "" or content_id < 1 or len(content_update) == 0:
        logger.error("API URL, token, content ID or update payload is invalid")
        return False

    resp = requests.put(
        f"{api_url}/v1/content/{content_id}",
        json=content_update,
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        logger.info("Content updated successfully")
        return True

    logger.error("Content update failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def delete_content(api_url: str, token: str, content_id: int) -> bool:
    """
    Delete content by ID.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :return: True if deletion succeeded; False otherwise
    """

    if api_url == "" or token == "" or content_id < 1:
        logger.error("API URL, token or content ID is invalid")
        return False

    resp = requests.delete(
        f"{api_url}/v1/content/{content_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        logger.info("Content deleted successfully")
        return True

    logger.error("Content deletion failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def create_content(
        api_url: str,
        token: str,
        title: str,
        description: str,
        source_id: int,
        tags: list[int],
        characters: list[int],
        authors: list[int],
        is_private: bool,
        files: dict[str, Any],
) -> bool:
    """
    Create content using multipart/form-data.
    :param api_url: API base URL
    :param token: Token
    :param title: Content title
    :param description: Content description
    :param source_id: Source ID
    :param tags: Tag IDs
    :param characters: Character IDs
    :param authors: Author IDs
    :param is_private: Whether content is private
    :param files: Multipart files map
    :return: True if creation succeeded; False otherwise
    """

    if api_url == "" or token == "" or len(files) == 0:
        logger.error("API URL, token or files payload is invalid")
        return False

    content_data = {
        "title": title,
        "description": description,
        "source_id": source_id,
        "tags": tags,
        "characters": characters,
        "authors": authors,
        "is_private": is_private,
    }
    
    form_data = {
        "content": json.dumps(content_data),
    }

    resp = requests.post(
        f"{api_url}/v1/content",
        data=form_data,
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        logger.info("Content created successfully")
        return True

    logger.error("Content creation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False



def get_content_thumb(api_url: str, token: str, content_id: int) -> bytes | None:
    """
    Get content thumb.
    :param api_url: API base URL
    :param token: Token
    :param content_id: Content ID
    :return: Raw thumb bytes or None
    """

    if api_url == "" or token == "" or content_id < 1:
        logger.error("API URL, token or content ID is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/content/{content_id}/thumb",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        logger.info("Content thumb retrieved successfully")
        return resp.content

    logger.error("Content thumb retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None
