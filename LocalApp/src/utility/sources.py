import logging
import requests
from src.models.sources import Source

logger = logging.getLogger()


def get_sources(api_url: str, token: str) -> list[Source] | None:
    """
    Get sources from server
    :param api_url: API base URL
    :param token: Token
    :return: List of Source objects or None
    """

    page_size = 20

    if api_url == "" or token == "":
        logger.error("API URL or token is invalid")
        return None

    url = f"{api_url}/v1/sources"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})

    if resp.status_code == 200:
        data = resp.json()
        sources = [Source.model_validate(item) for item in data]
        logger.info("Sources retrieved successfully")
        return sources

    logger.error("Sources retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def get_source_id(api_url: str, token: str, source_name: str) -> int | None:
    """
    Get source ID from server
    :param api_url: API base URL
    :param token: Token
    :param source_name: Source name
    :return: Source ID or None
    """

    if api_url == "" or token == "" or source_name == "":
        logger.error("API URL, token or source name is invalid")
        return None

    url = f"{api_url}/v1/sources/{source_name}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        data = resp.json()
        logger.info("Source ID retrieved successfully")
        return data.get("id")

    logger.error("Source ID retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def create_source(api_url: str, token: str, source_name: str) -> bool:
    """
    Create a source.
    :param api_url: API base URL
    :param token: Token
    :param source_name: Source name
    :return: False if creation failed; True if creation succeeded
    """

    if api_url == "" or token == "" or source_name == "":
        logger.error("API URL, token or source name is invalid")
        return False

    url = f"{api_url}/v1/sources?source_name={source_name}"
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        logger.info("Source created successfully")
        return True

    logger.error("Source creation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def edit_source(api_url: str, token: str, source_id: int, new_source_name: str) -> bool:
    """
    Edit a source
    :param api_url: API base URL
    :param token: Token
    :param source_id: Source ID
    :param new_source_name: New source name
    :return: False if edit failed; True if edit succeeded
    """

    if api_url == "" or token == "" or source_id < 1 or new_source_name == "":
        logger.error("API URL, token, source ID or new source name is invalid")
        return False

    url = f"{api_url}/v1/sources/{source_id}?source_name={new_source_name}"
    resp = requests.put(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        logger.info("Source edited successfully")
        return True

    logger.error("Source edit failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def delete_source(api_url: str, token: str, source_id: int) -> bool:
    """
    Delete a source
    :param api_url: API base URL
    :param token: Token
    :param source_id: Source ID
    :return: True if source deletion succeeded; False otherwise
    """

    if api_url == "" or token == "" or source_id < 1:
        logger.error("API URL, token or source ID is invalid")
        return False

    resp = requests.delete(
        f"{api_url}/v1/sources/{source_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Source deleted successfully")
        return True

    logger.error("Source deletion failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

