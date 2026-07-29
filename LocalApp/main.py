import argparse
from logging import Logger

from src.utility.logger import setlogger
import src.cli.console
import logging
from src.utility.config import config
import src.cli.login_commands as login_commands

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
    console.create_command("check_token", "Check if token is valid", login_commands.command_check_token)
    console.create_command("login", "Login to Nyapix and save token", login_commands.login)
    console.create_command("logout", "Logout from Nyapix and remove token", login_commands.logout)

    console.run()

else:
    logger.error("This file should not be imported as a module.")
    exit(1)
