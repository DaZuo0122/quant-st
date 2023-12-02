import datetime
import logging
import os

import colorlog

from utils.static import LOGS_FOLDER

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
s_handler = logging.StreamHandler()
s_handler.setLevel(logging.INFO)
log_formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s[%(asctime)s] - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={"DEBUG": "cyan", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red"},
)
s_handler.setFormatter(log_formatter)
logger.addHandler(s_handler)
if not os.path.exists(LOGS_FOLDER):
    os.mkdir(LOGS_FOLDER)
f_handler = logging.FileHandler(
    os.path.join(LOGS_FOLDER, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"), encoding="utf-8"
)
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(log_formatter)
logger.addHandler(f_handler)


def get_logger():
    return logger


def handle_caught_exception(e: Exception):
    logger.debug("Error", exc_info=(type(e), e, e.__traceback__))
