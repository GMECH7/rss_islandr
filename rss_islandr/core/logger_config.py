import logging
import re
import sys

GREEN = "\033[32m"  # Green
RED = "\033[31m"  # Red
PURPLE = "\033[35m"  # Purple
RESET_COLOR = "\033[0m"  # Reset color to default


def remove_color_codes(msg):
    """
    Function to remove color codes from log messages.
    """
    return re.sub(r"\033\[[0-9;]+m", "", msg)


class RemoveColorCodesFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        return remove_color_codes(msg)


def setup_logger(loger_level=logging.INFO):
    """
    Configures a logger to print to the console and a file.

    Format: LEVEL | YYYY-MM-DD HH:MM:s (UTC) | MESSAGE

    - Development (running .py script): Logs to console and file.
    - Production (running .exe): Logs are disabled.
    """
    is_executable = getattr(sys, "frozen", False)

    logger = logging.getLogger()
    if is_executable:  # Running as .exe, disable logging
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)

    else:
        logger.setLevel(loger_level)
        # Prevent adding duplicate handlers if this function is called more than once
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create a formatter with the specified UTC time format
        stream_formatter = logging.Formatter(
            f"%(asctime)s (UTC):: %(levelname)-5s :: {RESET_COLOR}%(message)s{RESET_COLOR}",
            "%Y-%m-%d %H:%M:%S",
        )

        # --- Console Handler ---
        # This handler prints logs to the console (standard output)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(stream_formatter)
        logger.addHandler(console_handler)

        # --- File Handler ---
        # This handler writes logs to the 'rss_islandr.log' file
        # mode='w' will overwrite the log file each time the application starts
        file_handler = logging.FileHandler("rss_islandr.log", mode="w")
        file_formatter = RemoveColorCodesFormatter(
            "%(asctime)s (UTC):: %(levelname)-5s :: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def logger_decorator(func):
    """A decorator to log function entry and exit points."""

    def wrapper(*args, **kwargs):
        logging.debug(f"{PURPLE}Start : {func.__module__}.{func.__name__} {RESET_COLOR}")
        result = func(*args, **kwargs)
        logging.debug(f"{GREEN}Finish: {func.__module__}.{func.__name__}{RESET_COLOR}")
        return result

    return wrapper
