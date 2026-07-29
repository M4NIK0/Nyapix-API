import logging
from typing import List
from src.utility.config import config
import src.utility.authors as authors_utils

logger = logging.getLogger(__name__)

def command_list_authors(args: List[str]):
    """
    List authors
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

    from src.utility.authors import get_authors

    authors = get_authors(api_url, token, page)
    if authors is not None:
        print(f"Authors (Page {page}/{authors.total_pages}):")
        for author in authors.authors:
            print(f"- {author.name} (ID: {author.id})")

def command_get_author_id(args: List[str]):
    """
    Get author id
    :param args: Author name (str)
    :return: None
    """
    api_url = config.get("api_url", "")
    token = config.get("token", "")
    if len(args) < 1:
        logger.error("Author name is missing")
        return

    full_name = ""
    for i in args:
        full_name += i + " "
    full_name = full_name.strip()
    id = authors_utils.get_author_id(api_url, token, full_name)
    if id is not None:
        print(f"Author ID: {id}")

def command_create_author(args: List[str]):
    """
    Create author
    :param args: Author name (str)
    :return: None
    """
    api_url = config.get("api_url", "")
    token = config.get("token", "")
    if len(args) < 1:
        logger.error("Author name is missing")
        return

    full_name = ""
    for i in args:
        full_name += i + " "
    full_name = full_name.strip()
    id = authors_utils.create_author(api_url, token, full_name)
    if id is not None:
        print(f"Author created with ID: {id}")

def command_update_author(args: List[str]):
    """
    Update author
    :param args: Author id (int), new author name (str)
    :return: None
    """
    api_url = config.get("api_url", "")
    token = config.get("token", "")
    if len(args) < 2:
        logger.error("Author name is missing")
        return
    try:
        author_id = int(args[0])
    except ValueError:
        logger.error("Author id is not an integer")
        return

    args = args[1:]
    full_name = ""
    for i in args:
        full_name += i + " "
    full_name = full_name.strip()
    res = authors_utils.edit_author(api_url, token, author_id, full_name)
    if not res:
        return
    else:
        print(f"Author updated with ID: {author_id}")

def command_delete_author(args: List[str]):
    """
    Delete author
    :param args: Author id (int)
    :return: None
    """
    api_url = config.get("api_url", "")
    token = config.get("token", "")
    if len(args) < 1:
        logger.error("Author id is missing")
        return

    try:
        author_id = int(args[0])
        res = authors_utils.delete_author(api_url, token, author_id)
        if not res:
            return
        else:
            print(f"Author deleted with ID: {author_id}")
    except ValueError:
        logger.error("Author id is not an integer")