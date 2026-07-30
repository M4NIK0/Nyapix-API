import logging

import requests

from src.models.tags import TagListModel

logger = logging.getLogger()

def get_tags(api_url: str, token: str, page: int) -> TagListModel | None:
    """
    Get tags from server
    :param api_url: API base URL
    :param token: Token
    :param page: Tags page number (starting from 1)
    :return: Dictionary of tags or None
    """

    page_size = 20

    if api_url == "" or token == "" or page < 1:
        logger.error("API URL, token or page is invalid")
        return None

    resp = requests.get(api_url + "/v1/tags?page=" + str(page), "&size=" + str(page_size), headers={"Authorization": f"Bearer {token}"})

    if resp.status_code == 200:
        resp = resp.json()
        tags = TagListModel.model_validate(resp)
        logger.info("Tags retrieved successfully (Page " + str(page) + ")")
        return tags

    return None

def search_tags(api_url: str, token: str, query: str, page: int) -> TagListModel | None:
    """
        Search tags on server
    :param api_url: API base URL
    :param token: Token
    :param query: Search query
    :param page: Tags page number (starting from 1)
    :return: TagListModel or None
    """

    page_size = 20

    if api_url == "" or token == "" or query == "":
        logger.error("API URL, token or query is invalid")
        return None

    resp = requests.get(api_url + "/v1/tags/search?tag_name=" + query + "&page=" + str(page) + "&max_results=" + str(page_size), headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        tags = TagListModel.model_validate(resp.json())
        logger.info("Tags retrieved successfully (Page " + str(page) + ")")
        return tags

    logger.error("Tags search failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None

def get_tag_id(api_url: str, token: str, tag_name: str) -> int | None:
    """
    Get tag ID from server
    :param api_url: API base URL
    :param token: Token
    :param tag_name: Tag name
    :return: Tag ID or None
    """

    if api_url == "" or token == "" or tag_name == "":
        logger.error("API URL, token or tag name is invalid")
        return None

    resp = requests.get(api_url + "/v1/tags/id/" + tag_name, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        resp = resp.json()
        logger.info("Tag ID retrieved successfully")
        return resp["id"]

    logger.error("Tag ID retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None

def create_tag(api_url: str, token: str, tag_name: str) -> bool:
    """
    Create a tag.
    :param api_url: API base URL
    :param token: Token
    :param tag_name: Tag name
    :return: False if tag creation failed (i.e. tag already exists or denied access);
    :return: True if tag creation succeeded
    """

    if api_url == "" or token == "" or tag_name == "":
        logger.error("API URL, token or tag name is invalid")
        return False

    resp = requests.post(api_url + "/v1/tags?tag_name=" + tag_name, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        logger.info("Tag created successfully")
        return True

    logger.error("Tag creation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

def edit_tag(api_url: str, token: str, tag_id: int, new_tag_name: str) -> bool:
    """
    Edit a tag
    :param api_url: API base URL
    :param token: Token
    :param tag_id: Tag ID
    :param new_tag_name: New tag name
    :return: False if tag creation failed (i.e. tag already exists or denied access);
    """

    if api_url == "" or token == "" or tag_id < 1 or new_tag_name == "":
        logger.error("API URL, token, tag ID or new tag name is invalid")
        return False

    resp = requests.put(api_url + "/v1/tags/" + str(tag_id) + "?tag_name=" + new_tag_name, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        logger.info("Tag edited successfully")
        return True

    logger.error("Tag edit failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def delete_tag(api_url: str, token: str, tag_id: int) -> bool:
    """
    Delete a tag
    :param api_url: API base URL
    :param token: Token
    :param tag_id: Tag ID
    :return: True if tag deletion succeeded; False otherwise
    """

    if api_url == "" or token == "" or tag_id < 1:
        logger.error("API URL, token or tag ID is invalid")
        return False

    resp = requests.delete(api_url + "/v1/tags/" + str(tag_id), headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        logger.info("Tag deleted successfully")
        return True

    logger.error("Tag deletion failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

def get_tag_name(api_url: str, token: str, tag_id: int) -> str | None:
    """
    Get tag name from server
    :param api_url: API base URL
    :param token: Token
    :param tag_id: Tag ID
    :return: Tag name or None
    """

    if api_url == "" or token == "" or tag_id < 1:
        logger.error("API URL, token or tag ID is invalid")
        return None

    resp = requests.get(api_url + "/v1/tags/" + str(tag_id), headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        resp = resp.json()
        logger.info("Tag name retrieved successfully")
        return resp["name"]

    logger.error("Tag name retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None