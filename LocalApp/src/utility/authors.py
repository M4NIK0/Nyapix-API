import logging

import requests

from src.models.authors import AuthorListModel

logger = logging.getLogger()


def get_authors(api_url: str, token: str, page: int) -> AuthorListModel | None:
    """
    Get authors from server
    :param api_url: API base URL
    :param token: Token
    :param page: Authors page number (starting from 1)
    :return: AuthorListModel or None
    """

    page_size = 20

    if api_url == "" or token == "" or page < 1:
        logger.error("API URL, token or page is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/authors?page={page}&size={page_size}",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 200:
        authors = AuthorListModel.model_validate(resp.json())
        logger.info("Authors retrieved successfully (Page " + str(page) + ")")
        return authors

    logger.error("Authors retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def search_authors(api_url: str, token: str, query: str, page: int) -> AuthorListModel | None:
    """
    Search authors on server
    :param api_url: API base URL
    :param token: Token
    :param query: Search query
    :param page: Authors page number (starting from 1)
    :return: AuthorListModel or None
    """

    page_size = 20

    if api_url == "" or token == "" or query == "":
        logger.error("API URL, token or query is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/authors/search?author_name={query}&page={page}&max_results={page_size}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        authors = AuthorListModel.model_validate(resp.json())
        logger.info("Authors retrieved successfully (Page " + str(page) + ")")
        return authors

    logger.error("Authors search failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def get_author_id(api_url: str, token: str, author_name: str) -> int | None:
    """
    Get author ID from server
    :param api_url: API base URL
    :param token: Token
    :param author_name: Author name
    :return: Author ID or None
    """

    if api_url == "" or token == "" or author_name == "":
        logger.error("API URL, token or author name is invalid")
        return None

    resp = requests.get(
        f"{api_url}/v1/authors/id/{author_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        data = resp.json()
        logger.info("Author ID retrieved successfully")
        return data["id"]

    logger.error("Author ID retrieval failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None


def create_author(api_url: str, token: str, author_name: str) -> bool:
    """
    Create an author.
    :param api_url: API base URL
    :param token: Token
    :param author_name: Author name
    :return: False if author creation failed; True if author creation succeeded
    """

    if api_url == "" or token == "" or author_name == "":
        logger.error("API URL, token or author name is invalid")
        return False

    resp = requests.post(
        f"{api_url}/v1/authors?author_name={author_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Author created successfully")
        return True

    logger.error("Author creation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False


def edit_author(api_url: str, token: str, author_id: int, new_author_name: str) -> bool:
    """
    Edit an author
    :param api_url: API base URL
    :param token: Token
    :param author_id: Author ID
    :param new_author_name: New author name
    :return: False if author edit failed; True if author edit succeeded
    """

    if api_url == "" or token == "" or author_id < 1 or new_author_name == "":
        logger.error("API URL, token, author ID or new author name is invalid")
        return False

    resp = requests.put(
        f"{api_url}/v1/authors/{author_id}?author_name={new_author_name}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        logger.info("Author edited successfully")
        return True

    logger.error("Author edit failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

