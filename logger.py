import logging
from config import LOG_TO_FILE, LOG_FILE_NAME


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if LOG_TO_FILE:
        file_handler = logging.FileHandler(LOG_FILE_NAME)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
