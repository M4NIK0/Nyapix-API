import getpass
import json
from typing import Union
import logging
import requests

logger = logging.getLogger(__name__)

def login(api_url: str, username: str, password: str) -> Union[str, None]:
    """
    Login function to get token from server using given credentials
    :param api_url: API base URL
    :param username: Username
    :param password: Password
    :return: Token as string if success, None otherwise
    """

    logger.info("Logging in")

    if username == "" or password == "":
        logger.error("Username or password is empty")
        return None
    resp = requests.post(api_url + "/v1/login", json={"username": username, "password": password})

    if resp.status_code == 200:
        logger.info("Login success")
        return resp.json()["access_token"]

    logger.error("Login failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return None

def logout(api_url: str, token: str) -> bool:
    """
    Logout function to invalidate token on server
    :param api_url: API base URL
    :param token: Token
    :return: True if success, False otherwise
    """

    logger.info("Logging out")

    if token == "":
        logger.error("Token is empty")
        return False

    resp = requests.delete(api_url + "/v1/logout", headers={"Authorization": "Bearer " + token})
    if resp.status_code == 200:
        logger.info("Logout success")
        return True

    logger.error("Logout failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False

def check_token(api_url: str, token: str) -> bool:
    """
    Check if token is valid
    :param api_url: API base URL
    :param token: Token
    :return: True if valid, False otherwise
    """

    if token == "":
        logger.error("Token is empty")
        return False

    resp = requests.get(api_url + "/v1/users/me", headers={"Authorization": "Bearer " + token})
    if resp.status_code == 200:
        logger.info("Token validation success")
        return True

    logger.error("Token validation failed (Error " + str(resp.status_code) + ")")
    logger.warning(resp.text)
    return False
