# utils.py

import logging
from rich.logging import RichHandler
from enum import Enum


class Format(Enum):
    START = "[bold][magenta]"
    END = START
    DEBUG = "[lightgrey]"
    INFO = "[cyan]"
    WARN = "[bold][orange]"
    ERROR = "[bold][red]"
    CRITICAL = ERROR


class Logger(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("rich")
        return cls._instance

    def start(self, message):
        self._instance.logger.info(Format.START.value + message + "[/]")

    def end(self, message):
        self._instance.logger.info(Format.END.value + message + "[/]")

    def debug(self, message):
        self._instance.logger.debug(Format.DEBUG.value + message + "[/]")

    def info(self, message):
        self._instance.logger.info(Format.INFO.value + message + "[/]")

    def warn(self, message):
        self._instance.logger.warning(Format.WARN.value + message + "[/]")

    def error(self, message):
        self._instance.logger.error(Format.ERROR.value + message + "[/]")

    def critical(self, message):
        self._instance.logger.critical(Format.CRITICAL.value + message + "[/]")

    @staticmethod
    def set_log_level(level):
        if level == "debug":
            level = logging.DEBUG
        elif level == "info":
            level = logging.INFO
        elif level == "warning":
            level = logging.WARNING
        elif level == "error":
            level = logging.ERROR
        elif level == "critical":
            level = logging.CRITICAL
        else:
            level = logging.INFO

        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        )
