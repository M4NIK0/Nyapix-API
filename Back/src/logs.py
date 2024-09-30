import logging

logger = logging.getLogger("main_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:\t%(message)s', '')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
