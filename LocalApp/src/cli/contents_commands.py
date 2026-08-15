import logging
import mimetypes
from typing import List
import os

from src.utility.misc import yes_no
from src.utility.tags import get_tags
from src.utility.config import config
from src.utility.characters import get_characters
from src.utility.authors import get_authors
from src.utility.tags import get_tag_name
from src.utility.authors import get_author_name
from src.utility.characters import get_character_name
from src.utility.sources import get_source_name, get_sources

import src.utility.contents as contents_utils

logger = logging.getLogger(__name__)

def command_upload_content(args: List[str]):
    """
    Upload content to database
    :param args: File path (string)
    :return: None
    """
    token = config.get("token", "")
    api_url = config.get("api_url", "")
    if token == "" or api_url == "":
        logger.error("No token or api_url provided")
        return

    if len(args) < 1:
        logger.error("File path is missing")
        return

    file_path = args[0]

    tags = []
    source = 0
    characters = []
    authors = []
    title = ""
    description = ""

    title = input("Title: ")
    description = input("Description: ")

    is_private = yes_no("Is this content private?")

    know_source_id = yes_no("Do you know the source ID?")
    know_tags_id = yes_no("Do you know all the tags ID?")
    know_authors_id = yes_no("Do you know all the authors ID?")
    know_characters_id = yes_no("Do you know all the characters ID?")

    if not know_source_id:
        sources = get_sources(api_url, token)
        if not sources:
            logger.error("Error getting sources")
            return

        for source in sources:
            print(f"{source.name} : {source.id}")
    done = False
    while not done:
        source = input("Source ID: ")
        try:
            source = int(source.strip())
            done = True
        except ValueError:
            print("Invalid input")

    if not know_tags_id:
        current_page = 1
        done = False
        while not done:
            tmptags = get_tags(api_url, token, current_page)
            if not tmptags:
                logger.error("Error getting tags")

            for tag in tmptags.tags:
                print(f"{tag.name} : {tag.id}")
            print("- 'n' for next page\n- 'p' for previous page and\n- number for a tag you want to add to the list\n- 'q' to finish")
            usrin = input("> ")
            if usrin == "n":
                current_page += 1
                continue
            elif usrin == "p" and current_page > 1:
                current_page -= 1
                continue
            elif usrin == "q":
                done = True
            else:
                try:
                    to_add = int(usrin.strip())
                    if to_add in tags:
                        raise ValueError
                    else:
                        tags.append(to_add)
                    tags.sort()
                    print("Current tags: " + ", ".join(str(tag) for tag in tags))
                except ValueError:
                    logger.error("Invalid input")
                    continue

    else:
        strtags = input("Tags ID (separated by comma): ")
        tags = [int(tag.strip()) for tag in strtags.split(",")]

    if not know_authors_id:
        current_page = 1
        done = False
        while not done:
            tmpauthors = get_authors(api_url, token, current_page)
            if not tmpauthors:
                logger.error("Error getting authors")

            for author in tmpauthors.authors:
                print(f"{author.name} : {author.id}")
            print("- 'n' for next page\n- 'p' for previous page and\n- number for an author you want to add to the list\n- 'q' to finish")
            usrin = input("> ")
            if usrin == "n":
                current_page += 1
                continue
            elif usrin == "p" and current_page > 1:
                current_page -= 1
                continue
            elif usrin == "q":
                done = True
            else:
                try:
                    to_add = int(usrin.strip())
                    if to_add in authors:
                        raise Exception
                    else:
                        authors.append(to_add)
                    authors.sort()
                    print("Current authors: " + ", ".join(str(author) for author in authors))
                except ValueError:
                    logger.error("Invalid input")
                    continue

    if not know_characters_id:
        current_page = 1
        done = False
        while not done:
            tmpcharacters = get_characters(api_url, token, current_page)
            if not tmpcharacters:
                logger.error("Error getting characters")
                return

            for character in tmpcharacters.characters:
                print(f"{character.name} : {character.id}")
            print("- 'n' for next page\n- 'p' for previous page and\n- number for a character you want to add to the list\n- 'q' to finish")
            usrin = input("> ")
            if usrin == "n":
                current_page += 1
                continue
            elif usrin == "p" and current_page > 1:
                current_page -= 1
                continue
            elif usrin == "q":
                done = True
            else:
                try:
                    to_add = int(usrin.strip())
                    if to_add in characters:
                        raise Exception
                    else:
                        characters.append(to_add)
                    characters.sort()
                    print("Current characters: " + ", ".join(str(character) for character in characters))
                except ValueError:
                    logger.error("Invalid input")
                    continue

    print(f"Title: {title}\nDescription: {description}\nAuthors: {', '.join(str(author) for author in authors)}\nCharacters: {', '.join(str(character) for character in characters)}\nSource: {source}\nTags: {', '.join(str(tag) for tag in tags)}")

    # Check the file exists
    if not os.path.exists(file_path):
        logger.error("File not found")
        return

    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        if file_size > 1000 * 1024 * 1024:  # 1000 MB
            logger.error("File size exceeds 100 MB")
            return
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        contents_utils.create_content(
            api_url,
            token,
            title,
            description,
            source,
            tags,
            characters,
            authors,
            is_private,
            {"file": (os.path.basename(file_path), f, mime_type)},
        )

def command_download_content(args: List[str]):
    """
    Download content from Nyapix using ID
    :param args: Content ID (int)
    :return: None
    """
    if len(args) < 1:
        logger.error("Content ID is required")
        return

    try:
        int(args[0])
    except ValueError:
        logger.error("Content ID is invalid")
        return

    content_id = int(args[0])

    token = config.get("token", "")
    api_url = config.get("api_url", "")
    download_folder = config.get("download_path", "")

    # Get content download URL
    content_info = contents_utils.get_content(api_url, token, content_id)
    if not content_info:
        logger.error("Content with this ID not found")
        return
    url = content_info.url
    print("Downloading content from url: " + url)

    # Download content from url
    contents_utils.download_content(url, token, download_folder + content_info.title)

def command_download_thumb(args: List[str]):
    """
    Download content thumbnails from Nyapix using ID(s)
    :param args: Content ID (int) (can put multiple IDs)
    :return:
    """
    if len(args) < 1:
        logger.error("At least one ID is required")
        return

    try:
        for i in args:
            int(i)
    except ValueError:
        logger.error("All IDs must be integers")
        return

    token = config.get("token", "")
    api_url = config.get("api_url", "")
    download_folder = config.get("download_path", "")

    for content_id in args:
        contents_utils.download_thumb(api_url, token, int(content_id), download_folder + "thumb_" + str(content_id))
        print("Downloaded thumbnail for ID " + str(content_id))

def command_content_mine(args: List[str]):
    """
    Get a list of my content
    :param args: Index of page (int)
    :return:
    """
    if len(args) < 1:
        logger.error("Page index is missing")
        return

    try:
        page = int(args[0])
    except ValueError:
        logger.error("Page index is not an integer")
        return

    token = config.get("token", "")
    api_url = config.get("api_url", "")

    contents = contents_utils.get_my_contents(api_url, token, page)
    print(contents)
    if contents is not None:
        print(f"My Contents (Page {page}/{contents.total_pages}):")
        for content in contents.contents:
            print(f"- {content.title} (ID: {content.id})")

def command_content_info(args: List[str]):
    """
    Get full information about an item
    :param args: Content ID (int)
    :return: None
    """
    if len(args) < 1:
        logger.error("Content ID is required")
        return

    try:
        int(args[0])
    except ValueError:
        logger.error("Content ID is invalid")
        return

    token = config.get("token", "")
    api_url = config.get("api_url", "")
    content_id = int(args[0])

    res = contents_utils.get_content(api_url, token, content_id)
    if not res:
        logger.error("Content with this ID not found")
        return

    content_tags = []

    for i in res.tags:
        tag_name = get_tag_name(api_url, token, i)
        if tag_name:
            content_tags.append(tag_name)

    content_authors = []

    for i in res.authors:
        author_name = get_author_name(api_url, token, i)
        if author_name:
            content_authors.append(author_name)

    content_characters = []

    for i in res.characters:
        character_name = get_character_name(api_url, token, i)
        if character_name:
            content_characters.append(character_name)

    source = get_source_name(api_url, token, res.source)

    print("Title: " + res.title)
    print("Description: " + res.description)
    print("Tags: " + ", ".join(content_tags))
    print("Characters: " + ", ".join(content_characters))
    print("Authors: " + ", ".join(content_authors))
    print("Source: " + source)

def command_content_delete(args: List[str]):
    """
    Delete content from Nyapix using ID
    :param args: Content ID (int)
    :return: None
    """
    if len(args) < 1:
        logger.error("Content ID is required")
        return

    try:
        int(args[0])
    except ValueError:
        logger.error("Content ID is invalid")
        return

    content_id = int(args[0])

    token = config.get("token", "")
    api_url = config.get("api_url", "")

    contents_utils.delete_content(api_url, token, content_id)
