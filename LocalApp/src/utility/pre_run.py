import json, os
import logging

logger = logging.getLogger(__name__)

def load_config() -> dict:
    """
    Loads configuration from config.json and returns it as a dict, defaults and creates the file if not found.
    :return:
    """
    config = {}
    default_config = {}
    if not os.path.isfile("config.json"):
        default_config = {
            "token": None,
            "api_url": "https://api.example.com",
            "max_thumbs": 5,
            "download_path": "./downloads",
            "db_path": "./database.db"
        }
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)

    with open('config.json', 'r') as f:
        config = json.load(f)

    if "token" not in config or "api_url" not in config or "max_thumbs" not in config or "download_path" not in config or "db_path" not in config:
        logger.error("Missing required configuration parameters.")
        raise ValueError("Missing required configuration parameters.")

    logger.info("Configuration loaded successfully.")

    return config

def save_config(config: dict) -> None:
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)