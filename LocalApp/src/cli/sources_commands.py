import logging
from typing import List

from src.utility.config import config
import src.utility.sources as sources_utils

logger = logging.getLogger(__name__)


def command_list_sources(args: List[str]):
    """
    List sources
    :param args: Empty list
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    sources = sources_utils.get_sources(api_url, token)
    if sources is not None:
        print("Sources:")
        for source in sources:
            print(f"- {source.name} (ID: {source.id})")


def command_get_source_id(args: List[str]):
    """
    Get source id
    :param args: Source name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Source name is missing")
        return

    full_name = " ".join(args).strip()
    source_id = sources_utils.get_source_id(api_url, token, full_name)
    if source_id is not None:
        print(f"Source ID: {source_id}")


def command_create_source(args: List[str]):
    """
    Create source
    :param args: Source name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Source name is missing")
        return

    full_name = " ".join(args).strip()
    res = sources_utils.create_source(api_url, token, full_name)
    if res:
        print(f"Source created: {full_name}")


def command_update_source(args: List[str]):
    """
    Update source
    :param args: Source id (int), new source name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 2:
        logger.error("Source id or new name is missing")
        return

    try:
        source_id = int(args[0])
    except ValueError:
        logger.error("Source id is not an integer")
        return

    new_name = " ".join(args[1:]).strip()
    res = sources_utils.edit_source(api_url, token, source_id, new_name)
    if res:
        print(f"Source updated with ID: {source_id}")


def command_delete_source(args: List[str]):
    """
    Delete source
    :param args: Source id (int)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Source id is missing")
        return

    try:
        source_id = int(args[0])
    except ValueError:
        logger.error("Source id is not an integer")
        return

    res = sources_utils.delete_source(api_url, token, source_id)
    if res:
        print(f"Source deleted with ID: {source_id}")

