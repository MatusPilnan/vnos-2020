import asyncio
import os
from asyncio import Queue
from logging.handlers import TimedRotatingFileHandler, QueueHandler

from quart.logging import default_handler

from varpivo.config import config
from varpivo.utils.network import ServerSentEvent


def get_log_file():
    os.makedirs(config.LOG_FOLDER, exist_ok=True)
    return os.path.join(config.LOG_FOLDER, config.LOG_FILE)


def setup_logger(logger):
    logger.setLevel('INFO')
    file = get_log_file()
    handler = TimedRotatingFileHandler(filename=file, encoding='utf-8', when='midnight', backupCount=7)
    handler.setFormatter(default_handler.formatter)
    handler.setLevel('INFO')
    logger.addHandler(handler)


async def html_log_reader():
    with open(get_log_file(), mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            yield f'<p style="margin: 0">{line}</p>'.encode('utf-8')


async def log_reader(encode=True):
    with open(get_log_file(), mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            if encode:
                yield line.encode('utf-8')
            else:
                yield line


async def stream_log_reader(logger):
    queue = Queue()
    handler = QueueHandler(queue)
    logger.addHandler(handler)
    formatter = default_handler.formatter
    while queue is not None:
        try:
            entry = formatter.format(await queue.get())
            yield ServerSentEvent(entry).encode()
        except asyncio.CancelledError:
            logger.removeHandler(handler)
            queue = None
