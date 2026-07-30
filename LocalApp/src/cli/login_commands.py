import logging
from typing import List
from src.utility.login import check_token, logout as logout_func, login as login_func
from src.utility.pre_run import save_config
from src.utility.config import config

logger = logging.getLogger(__name__)

def command_check_token(args: List[str]):
    """
    Check if token is valid
    :param args: Empty list
    :return: None
    """

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if token == "":
        logger.error("Token is empty")
        return

    if check_token(api_url, token):
        print("Token is valid")
    else:
        logger.error("Token is invalid")

def command_login(args: List[str]):
    """
    Loging to nyapix and save token
    :param args: Username and password as string
    :return: None
    """

    if len(args) < 2:
        logger.error("Username or password is missing")
        return

    username = args[0]
    password = args[1]


    api_url = config.get("api_url", "")
    token = login_func(api_url, username, password)

    if token is not None:
        config["token"] = token
        save_config(config)
        print("Login success")
    else:
        logger.error("Login failed")

def command_logout(args: List[str]):
    """
    Logout from nyapix and save token
    :param args: Empty list
    :return: None
    """
    api_url = config.get("api_url", "")
    token = config.get("token", "")

    if token == "":
        logger.error("Token is empty")
        return
    logout_func(api_url, token)

    config["token"] = None
    save_config(config)
    logger.warning("Logout success")
