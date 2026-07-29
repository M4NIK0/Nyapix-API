import argparse

from src.utility.logger import setlogger
import src.cli.console
import logging
import src.cli.login_commands as login_commands
import src.cli.authors_commands as authors_commands
import src.cli.tags_commands as tags_commands
import src.cli.sources_commands as sources_commands
import src.cli.characters_commands as characters_commands
import src.cli.config_commands as config_commands

logger = logging.getLogger("main")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="NyapixClient",
        description="A client for interacting with the Nyapix API.",
        epilog="For any questions or issues, please contact me on GitHub or open an issue.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-t", "--token", help="Nyapix API token")
    parser.add_argument("-l", "--log", help="Log level applied (0-5)", type=int, choices=range(0, 2), default=2)
    parser.add_argument("-u", "--url", help="API URL")

    arguments = parser.parse_args()
    setlogger(arguments.log)

    # logger.info("App started")
    # print(get_characters(config["api_url"], config["token"], 1))
    # print(search_characters(config["api_url"], config["token"], "cu", 1))
    # print(create_character(config["api_url"], config["token"], "test_character"))
    # print(get_characters(config["api_url"], config["token"], 1))
    # print(get_character_id(config["api_url"], config["token"], "test_character"))

    console = src.cli.console.Console()
    console.create_command("config_reload", "Reload configuration", [], config_commands.command_reload_config, "Configuration")
    console.create_command("config_show", "Show configuration", [], config_commands.command_show_config,"Configuration")
    console.create_command("config_set_api_uri", "Set API URI", ["url"], config_commands.command_set_api_uri, "Configuration")

    console.create_command("check_token", "Check if token is valid", [], login_commands.command_check_token, "Login to Nyapix")
    console.create_command("login", "Login to Nyapix and save token", [], login_commands.command_login, "Login to Nyapix")
    console.create_command("logout", "Logout from Nyapix and remove token", [], login_commands.command_logout, "Login to Nyapix")

    console.create_command("author_list", "List authors (page id starts at 1)", ["page"], authors_commands.command_list_authors, "Authors")
    console.create_command("author_search", "Search authors by name (page id starts at 1)", ["name", "page"], authors_commands.command_search_author, "Authors")
    console.create_command("author_id", "Get author id by name", ["name"], authors_commands.command_get_author_id, "Authors")
    console.create_command("author_create", "Create author by name", ["name"], authors_commands.command_create_author, "Authors")
    console.create_command("author_update", "Change an author's name", ["id", "name"], authors_commands.command_update_author, "Authors")
    console.create_command("author_delete", "Delete an author by id", ["id"], authors_commands.command_delete_author, "Authors")

    console.create_command("tag_list", "List tags (page id starts at 1)", ["page"], tags_commands.command_list_tags, "Tags")
    console.create_command("tag_search", "Search tags by name (page id starts at 1)", ["name", "page"], tags_commands.command_search_tag, "Tags")
    console.create_command("tag_id", "Get tag id by name", ["name"], tags_commands.command_get_tag_id, "Tags")
    console.create_command("tag_create", "Create tag by name", ["name"], tags_commands.command_create_tag, "Tags")
    console.create_command("tag_update", "Change a tag's name", ["id", "name"], tags_commands.command_update_tag, "Tags")
    console.create_command("tag_delete", "Delete a tag by id", ["id"], tags_commands.command_delete_tag, "Tags")

    console.create_command("source_list", "List sources", [], sources_commands.command_list_sources, "Sources")
    console.create_command("source_id", "Get source id by name", ["name"], sources_commands.command_get_source_id, "Sources")
    console.create_command("source_create", "Create source by name", ["name"], sources_commands.command_create_source, "Sources")
    console.create_command("source_update", "Change a source's name", ["id", "name"], sources_commands.command_update_source, "Sources")
    console.create_command("source_delete", "Delete a source by id", ["id"], sources_commands.command_delete_source, "Sources")

    console.create_command("character_list", "List characters (page id starts at 1)", ["page"], characters_commands.command_list_characters, "Characters")
    console.create_command("character_search", "Search characters by name (page id starts at 1)", ["name", "page"], characters_commands.command_search_character, "Characters")
    console.create_command("character_id", "Get character id by name", ["name"], characters_commands.command_get_character_id, "Characters")
    console.create_command("character_create", "Create character by name", ["name"], characters_commands.command_create_character, "Characters")
    console.create_command("character_update", "Change a character's name", ["id", "name"], characters_commands.command_update_character, "Characters")
    console.create_command("character_delete", "Delete a character by id", ["id"], characters_commands.command_delete_character, "Characters")

    console.run()

else:
    logger.error("This file should not be imported as a module.")
    exit(1)
