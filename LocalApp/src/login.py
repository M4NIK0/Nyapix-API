import getpass
import json
from typing import Union
import logging

logger = logging.getLogger(__name__)

# TODO: Add real login
# Login function to get token from server
def login() -> Union[str, None]:
    success = False
    token = ""
    while not success:
        username = input("Username: ")
        password = getpass.getpass("Password: ", echo_char="*")

        # Request here login
        print("Logging in...")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoyLCJ1c2VyX2lkIjoxfQ.0DUrHmrnkkRpMRWZsIBg6v6VjJdoGGzXBxrHA2Ip79g"
        success = True
        logger.info("Successfully logged in")
        print("Login successful")

    success = False
    while not success:
        save = input("Do you want to save the credentials? (In config.json) [y/n]: ").lower()
        if save == "y":
            cfg = json.load(open("config.json", "r"))
            cfg["token"] = token
            json.dump(cfg, open("config.json", "w"))
            logger.info("Saved credentials")
            print("Saved credentials")
            success = True
        elif save == "n":
            logger.info("Credentials not saved")
            success = True

    return token
