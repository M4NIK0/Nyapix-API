import json, os
import argparse
import logging

config = {}

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
    raise ValueError("Missing required configuration parameters.")

parser = argparse.ArgumentParser(
    prog="NyapixClient",
    description="A client for interacting with the Nyapix API.",
    epilog="For any questions or issues, please contact me on GitHub or open an issue.",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument("-t", "--token", help="Nyapix API token")
parser.add_argument("-l", "--log", help="Log level applied (0-5)", type=int, choices=range(0, 6), default=3)

parser.parse_args()