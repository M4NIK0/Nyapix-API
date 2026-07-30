import logging
from typing import List
import src.utility.config
from src.utility.pre_run import load_config
from src.utility.pre_run import save_config

logger = logging.getLogger(__name__)

def command_show_config(args: List[str]):
    """
    Shows configuration information
    :param args: Empty list
    :return: None
    """
    logger.info("Showing configuration:")
    for key, value in src.utility.config.config.items():
        if key == "token":
            print(f"{key}: <hidden>")
        else:
            print(f"{key}: {value}")

def command_reload_config(args: List[str]):
    """
    Reloads configuration
    :param args: Empty list
    :return: None
    """
    src.utility.config.config = load_config()
    logger.info("Configuration reloaded successfully.")

def command_set_api_uri(args: List[str]):
    """
    Sets API URI
    :param args: API URI as string (https://example.com:5000/)
    :return: None
    """
    if len(args) < 1:
        logger.error("API URI is missing")
        return

    # Check URI format
    if not args[0].startswith("http://") and not args[0].startswith("https://"):
        logger.error("API URI must start with http:// or https://")
        return
    if args[0].endswith("/"):
        args[0] = args[0][:-1]

    src.utility.config.config["api_url"] = args[0]
    save_config(src.utility.config.config)

    logger.info(f"API URI set to {args[0]}")
    print("Do not forget to check your token validity with 'check_token' command after changing the API URI.")