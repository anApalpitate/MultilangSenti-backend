import logging
import os
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

from config import get_config

init(autoreset=True)

# ====== 配置 ======
log_dir = get_config().LOG_PATH
os.makedirs(log_dir, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s]   (%(module)s.%(funcName)s:%(lineno)d)  - %(message)s"
DATE_FORMAT = "%m-%d %H:%M"


class ColorFormatter(logging.Formatter):
    """
    自定义日志格式化器，基于日志级别为控制台日志添加颜色。
    """
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


def create_file_handler(filename: str, level: int, formatter: logging.Formatter, enable_file: bool = True):
    """
    创建一个带有日志轮转功能的文件日志处理器
    @:param filename: 日志文件名
    @:param level: 日志等级
    @:param formatter: 日志格式化器
    @:param enable_file: 是否启用文件日志处理
    @:return: logging.Handler | None
    """
    if not enable_file:
        return None
    handler = RotatingFileHandler(
        os.path.join(log_dir, filename),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def create_stream_handler(level: int, enable_stream: bool = True, enable_color: bool = True):
    """
   创建一个用于控制台输出的日志处理器。
   @:param level: 日志等级
   @:param enable_stream: 是否启用控制台日志输出
   @:param enable_color: 是否启用彩色输出
   @:return: 控制台日志处理器或 None
   """
    if not enable_stream:
        return None
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = ColorFormatter(LOG_FORMAT, DATE_FORMAT) if enable_color else logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def build_logger(name: str, level: int, filename: str,
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
    """
    自定义日志类
    """

    def __init__(self):
        self._info = build_logger("info", logging.INFO, "info.log")
        self._debug = build_logger("debug", logging.DEBUG, "debug.log")
        self._error = build_logger("error", logging.ERROR, "error.log")

    @staticmethod
    def _log(level_logger, msg, *args, prefix="", stacklevel=3, **kwargs):
        if prefix:
            msg = prefix + msg
        level_logger.log(level_logger.level, msg, *args, stacklevel=stacklevel, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(self._info, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        from config import get_config
        config = get_config()
        if config.DEBUG:
            self._log(self._debug, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(self._error, msg, *args, **kwargs)


log = Logger()  # 导出日志实例类


def log_init(clear=False):
    build_logger("uvicorn.access", logging.INFO, "access.log", enable_stream=False)
    build_logger("uvicorn.error", logging.WARNING, "error.log")
    if clear:
        log_clean()
    log.info("🌊日志初始化完成")


def log_clean():
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8"):
                pass
