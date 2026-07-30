import logging
from typing import List

from src.utility.config import config
import src.utility.characters as characters_utils

logger = logging.getLogger(__name__)


def command_list_characters(args: List[str]):
    """
    List characters
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

    characters = characters_utils.get_characters(api_url, token, page)
    if characters is not None:
        print(f"Characters (Page {page}/{characters.total_pages}):")
        for character in characters.characters:
            print(f"- {character.name} (ID: {character.id})")


def command_search_character(args: List[str]):
    """
    Search character
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

    res = characters_utils.search_characters(api_url, token, args[0], page)
    if res is not None:
        print(f"Characters (Page {page}/{res.total_pages}):")
        for character in res.characters:
            print(f"- {character.name} (ID: {character.id})")


def command_get_character_id(args: List[str]):
    """
    Get character id
    :param args: Character name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Character name is missing")
        return

    full_name = " ".join(args).strip()
    character_id = characters_utils.get_character_id(api_url, token, full_name)
    if character_id is not None:
        print(f"Character ID: {character_id}")


def command_create_character(args: List[str]):
    """
    Create character
    :param args: Character name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Character name is missing")
        return

    full_name = " ".join(args).strip()
    res = characters_utils.create_character(api_url, token, full_name)
    if res:
        print(f"Character created: {full_name}")


def command_update_character(args: List[str]):
    """
    Update character
    :param args: Character id (int), new character name (str)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 2:
        logger.error("Character id or new name is missing")
        return

    try:
        character_id = int(args[0])
    except ValueError:
        logger.error("Character id is not an integer")
        return

    new_name = " ".join(args[1:]).strip()
    res = characters_utils.edit_character(api_url, token, character_id, new_name)
    if res:
        print(f"Character updated with ID: {character_id}")


def command_delete_character(args: List[str]):
    """
    Delete character
    :param args: Character id (int)
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if len(args) < 1:
        logger.error("Character id is missing")
        return

    try:
        character_id = int(args[0])
    except ValueError:
        logger.error("Character id is not an integer")
        return

    res = characters_utils.delete_character(api_url, token, character_id)
    if res:
        print(f"Character deleted with ID: {character_id}")

