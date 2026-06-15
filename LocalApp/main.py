import argparse
from src.utility.logger import setlogger
import logging

import src.utility.pre_run as pre_run
from utility.tags import get_tags

config = {}
logger = logging.getLogger("main")

if __name__ == "__main__":
    config = pre_run.load_config()

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

    logger.info("App started")
    print(get_tags(config["api_url"], config["token"], 1))

else:
    logger.error("This file should not be imported as a module.")
    exit(1)
