import logging
from typing import List
import os

from src.utility.misc import yes_no
from src.utility.sources import get_sources
from src.utility.tags import get_tags
from src.utility.config import config
from src.utility.characters import get_characters
from src.utility.authors import get_authors

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
                        raise Exception
                    else:
                        tags.append(to_add)
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
                except ValueError:
                    logger.error("Invalid input")
                    continue

    print(f"Title: {title}\nDescription: {description}\nAuthors: {', '.join(str(author) for author in authors)}\nCharacters: {', '.join(str(character) for character in characters)}\nSource: {source}\nTags: {', '.join(str(tag) for tag in tags)}")

    # Check the file exists
    if not os.path.exists(file_path):
        logger.error("File not found")
        return

    contents_utils.create_content(api_url, token, title, description, authors, characters, source, tags, file_path, is_private, 