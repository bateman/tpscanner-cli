"""Logger class for logging messages with rich formatting."""

import logging
from enum import Enum
from typing import ClassVar

from rich.logging import RichHandler


class Format(Enum):
    """Enum class for message formatting."""

    START = "[bold][magenta]"
    END = START
    DEBUG = "[dim][grey]"
    INFO = "[cyan]"
    WARN = "[bold][orange]"
    ERROR = "[bold][red]"
    CRITICAL = ERROR


class Logger(object):
    """Singleton class for logging messages with rich formatting."""

    _instance: ClassVar = None

    def __new__(cls):
        """Create a new instance of the Logger class if it does not exist."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("rich")
        return cls._instance

    def start(self, message: str) -> None:
        """Log the start of a process.

        Arguments:
            message (str): The message to be logged.

        """
        self._instance.logger.info(Format.START.value + message + "[/]")

    def end(self, message: str) -> None:
        """Log the end of a process.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.info(Format.END.value + message + "[/]")

    def debug(self, message: str) -> None:
        """Log a debug message.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.debug(Format.DEBUG.value + message + "[/]")

    def info(self, message: str) -> None:
        """Log an info message.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.info(Format.INFO.value + message + "[/]")

    def warn(self, message: str) -> None:
        """Log a warning message.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.warning(Format.WARN.value + message + "[/]")

    def error(self, message: str) -> None:
        """Log an error message.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.error(Format.ERROR.value + message + "[/]")

    def critical(self, message: str) -> None:
        """Log a critical message.

        Arguments:
        message (str): The message to be logged.

        """
        self._instance.logger.critical(Format.CRITICAL.value + message + "[/]")

    @staticmethod
    def set_log_level(level: int) -> None:
        """Set the logging level for the logger.

        Arguments:
            level (int): The logging level.

        """
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
        elif level == "none":
            level = logging.CRITICAL + 1
        else:
            level = logging.WARNING

        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        )
