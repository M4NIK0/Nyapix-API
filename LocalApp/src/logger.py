import logging

filename = 'logs/app.log'

# Setup logger
def setlogger(level: int):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)

    # Set log level for file
    if level == 0:
        fh.setLevel(logging.ERROR)
    elif level == 1:
        fh.setLevel(logging.WARNING)
    elif level == 2:
        fh.setLevel(logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
