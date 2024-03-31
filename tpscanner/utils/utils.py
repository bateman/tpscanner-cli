"""Utility functions for the TPScanner."""

import random
import time


def sleep(interval: int) -> None:
    """Sleep for the specified interval plus a random amount of time between 0 and 1 second.

    Arguments:
        interval (int): The interval to sleep for.

    """
    time.sleep(interval + random.randint(0, 1))  # noqa S311
