import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from eircode.constants import LOG_LOCATION


FORMAT = '%(asctime)s|%(levelname)s| %(message)s'


class ColourfulFormatter(logging.Formatter):

    cyan = "\x1b[36m;21m"
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = FORMAT
    format_problematic = FORMAT + ' (%(filename)s:%(lineno)d)'

    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format_problematic + reset,
        logging.ERROR: red + format_problematic + reset,
        logging.CRITICAL: bold_red + format_problematic + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.Logger('road_collisions', logging.DEBUG)

os.makedirs(
    os.path.dirname(LOG_LOCATION),
    exist_ok=True
)

handler = RotatingFileHandler(
    LOG_LOCATION,
    maxBytes=1000000,
    backupCount=20
)
handler.setFormatter(
    logging.Formatter(
        fmt='%(asctime)s|%(levelname)s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)
logger.addHandler(handler)

std_handler = logging.StreamHandler(sys.stdout)
std_handler.setFormatter(
    ColourfulFormatter()
)
logger.addHandler(std_handler)
