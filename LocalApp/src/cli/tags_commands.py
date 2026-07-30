import logging
from typing import List

from src.utility.config import config
import src.utility.tags as tags_utils

logger = logging.getLogger(__name__)


def command_list_tags(args: List[str]):
    """
    List tags
    :param args: Index of page (int)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Page index is missing")
        return

    try:
        page = int(args[0])
    except ValueError:
        logger.error("Page index is not an integer")
        return

    tags = tags_utils.get_tags(api_url, token, page)
    if tags is not None:
        print(f"Tags (Page {page}/{tags.total_pages}):")
        for tag in tags.tags:
            print(f"- {tag.name} (ID: {tag.id})")


def command_search_tag(args: List[str]):
    """
    Search tag
    :param args: Query (str), page (int)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 2:
        logger.error("Query or page is missing")
        return

    try:
        page = int(args[1])
    except ValueError:
        logger.error("Page is not an integer")
        return

    res = tags_utils.search_tags(api_url, token, args[0], page)
    if res is not None:
        print(f"Tags (Page {page}/{res.total_pages}):")
        for tag in res.tags:
            print(f"- {tag.name} (ID: {tag.id})")


def command_get_tag_id(args: List[str]):
    """
    Get tag id
    :param args: Tag name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Tag name is missing")
        return

    full_name = " ".join(args).strip()
    tag_id = tags_utils.get_tag_id(api_url, token, full_name)
    if tag_id is not None:
        print(f"Tag ID: {tag_id}")


def command_create_tag(args: List[str]):
    """
    Create tag
    :param args: Tag name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Tag name is missing")
        return

    full_name = " ".join(args).strip()
    res = tags_utils.create_tag(api_url, token, full_name)
    if res:
        print(f"Tag created: {full_name}")


def command_update_tag(args: List[str]):
    """
    Update tag
    :param args: Tag id (int), new tag name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 2:
        logger.error("Tag id or new name is missing")
        return

    try:
        tag_id = int(args[0])
    except ValueError:
        logger.error("Tag id is not an integer")
        return

    new_name = " ".join(args[1:]).strip()
    res = tags_utils.edit_tag(api_url, token, tag_id, new_name)
    if res:
        print(f"Tag updated with ID: {tag_id}")


def command_delete_tag(args: List[str]):
    """
    Delete tag
    :param args: Tag id (int)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Tag id is missing")
        return

    try:
        tag_id = int(args[0])
    except ValueError:
        logger.error("Tag id is not an integer")
        return

    res = tags_utils.delete_tag(api_url, token, tag_id)
    if res:
        print(f"Tag deleted with ID: {tag_id}")

