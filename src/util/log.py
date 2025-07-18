import logging
import os
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

init(autoreset=True)

# ====== 配置 ======
LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s]   (%(module)s.%(funcName)s:%(lineno)d)  - %(message)s"
DATE_FORMAT = "%m-%d %H:%M"


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        return f"{color}{super().format(record)}{Style.RESET_ALL}"


def create_file_handler(filename, level, formatter, enable_file=True):
    if not enable_file:
        return None
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def create_stream_handler(level, enable_stream=True, enable_color=True):
    if not enable_stream:
        return None
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = ColorFormatter(LOG_FORMAT, DATE_FORMAT) if enable_color else logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def build_logger(name, level, filename,
                 enable_stream=True,
                 enable_file=True):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    file_handler = create_file_handler(
        filename, level, logging.Formatter(LOG_FORMAT, DATE_FORMAT), enable_file
    )
    stream_handler = create_stream_handler(level, enable_stream)

    if file_handler:
        logger.addHandler(file_handler)
    if stream_handler:
        logger.addHandler(stream_handler)

    return logger


class Logger:
    def __init__(self):
        self._all = build_logger("all", logging.DEBUG, "all.log", enable_stream=False)
        self._info = build_logger("info", logging.INFO, "info.log")
        self._debug = build_logger("debug", logging.DEBUG, "debug.log")
        self._error = build_logger("error", logging.ERROR, "error.log")

    def _log(self, level_logger, msg, *args, prefix="", stacklevel=3, **kwargs):
        if prefix:
            msg = prefix + msg
        level_logger.log(level_logger.level, msg, *args, stacklevel=stacklevel, **kwargs)
        self._all.log(level_logger.level, msg, *args, stacklevel=stacklevel, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(self._info, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        from config import get_config
        config = get_config()
        if config.DEBUG:
            self._log(self._debug, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(self._error, msg, *args, **kwargs)


# 导出实例类
log = Logger()


def log_init(clear=False):
    build_logger("uvicorn.access", logging.INFO, "access.log", enable_stream=False)
    build_logger("uvicorn.error", logging.WARNING, "error.log")
    if clear:
        log_clean()


def log_clean():
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8"):
                pass
