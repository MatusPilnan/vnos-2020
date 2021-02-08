import os
from logging.handlers import RotatingFileHandler

from quart.logging import default_handler

from varpivo.config import config


def get_log_file():
    os.makedirs(config.LOG_FOLDER, exist_ok=True)
    return os.path.join(config.LOG_FOLDER, config.LOG_FILE)


def setup_logger(logger):
    logger.setLevel('INFO')
    file = get_log_file()
    handler = RotatingFileHandler(filename=file, encoding='utf-8', maxBytes=50000, backupCount=1)
    handler.setFormatter(default_handler.formatter)
    handler.setLevel('INFO')
    logger.addHandler(handler)


async def html_log_reader():
    with open(get_log_file(), mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            yield f'<p style="margin: 0">{line}</p>'.encode('utf-8')
