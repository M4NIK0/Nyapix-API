from logging.handlers import RotatingFileHandler
import logging

logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)  # Set the logger's level to DEBUG
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler('logs/nyapix.log', maxBytes=1024*1024, backupCount=5)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
