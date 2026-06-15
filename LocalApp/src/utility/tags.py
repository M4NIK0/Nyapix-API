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
    :return: Dictionary of tags or None
    """

    page_size = 20

    if api_url == "" or token == "" or query == "":
        logger.error("API URL, token or query is invalid")
        return None

    resp = requests.get(api_url + "/v1/tags/search?tag_name=" + query + "&page=" + str(page) + "&max_results=" + str(page_size), headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        resp = resp.json()
        logger.info("Tags retrieved successfully (Page " + str(page) + ")")
        return resp

    return None