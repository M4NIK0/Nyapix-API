import logging

import requests

from src.models.characters import CharacterListModel

logger = logging.getLogger()


def get_characters(api_url: str, token: str, page: int) -> CharacterListModel | None:
    """
    Get characters from server
    :param api_url: API base URL
    :param token: Token
    :param page: Characters page number (starting from 1)
    :return: CharacterListModel or None
    """

    page_size = 20

    if api_url == "" or token == "" or page < 1:
        logger.error("API URL, token or page is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/characters?page={page}&size={page_size}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        characters = CharacterListModel.model_validate(resp.json())
        logger.info("Characters retrieved successfully (Page " + str(page) + ")")
        return characters

    logger.error("Characters retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def search_characters(api_url: str, token: str, query: str, page: int) -> CharacterListModel | None:
    """
    Search characters on server
    :param api_url: API base URL
    :param token: Token
    :param query: Search query
    :param page: Characters page number (starting from 1)
    :return: CharacterListModel or None
    """

    page_size = 20

    if api_url == "" or token == "" or query == "":
        logger.error("API URL, token or query is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/characters/search?character_name={query}&page={page}&max_results={page_size}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        characters = CharacterListModel.model_validate(resp.json())
        logger.info("Characters retrieved successfully (Page " + str(page) + ")")
        return characters

    logger.error("Characters search failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def get_character_id(api_url: str, token: str, character_name: str) -> int | None:
    """
    Get character ID from server
    :param api_url: API base URL
    :param token: Token
    :param character_name: Character name
    :return: Character ID or None
    """

    if api_url == "" or token == "" or character_name == "":
        logger.error("API URL, token or character name is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/characters/id/{character_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        data = resp.json()
        logger.info("Character ID retrieved successfully")
        return data["id"]

    logger.error("Character ID retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def create_character(api_url: str, token: str, character_name: str) -> bool:
    """
    Create a character.
    :param api_url: API base URL
    :param token: Token
    :param character_name: Character name
    :return: False if character creation failed; True if character creation succeeded
    """

    if api_url == "" or token == "" or character_name == "":
        logger.error("API URL, token or character name is invalid")
        return False

    resp = requests.post(
        f"{api_url}/v1/characters?character_name={character_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Character created successfully")
        return True

    logger.error("Character creation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def edit_character(api_url: str, token: str, character_id: int, new_character_name: str) -> bool:
    """
    Edit a character
    :param api_url: API base URL
    :param token: Token
    :param character_id: Character ID
    :param new_character_name: New character name
    :return: False if character edit failed; True if character edit succeeded
    """

    if api_url == "" or token == "" or character_id < 1 or new_character_name == "":
        logger.error("API URL, token, character ID or new character name is invalid")
        return False

    resp = requests.put(
        f"{api_url}/v1/characters/{character_id}?character_name={new_character_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Character edited successfully")
        return True

    logger.error("Character edit failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

def delete_character(api_url: str, token: str, character_id: int) -> bool:
    """
    Delete a character
    :param api_url: API base URL
    :param token: Token
    :param character_id: Character ID
    :return: True if character deletion succeeded, False otherwise
    """

    if api_url == "" or token == "" or character_id < 1:
        logger.error("API URL, token or character ID is invalid")
        return False

    resp = requests.delete(
        f"{api_url}/v1/characters/{character_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Character deleted successfully")
        return True

    logger.error("Character deletion failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False
