import logging
import sys
import time


class UTCFormatter(logging.Formatter):
    """A custom formatter to ensure timestamps are in UTC."""

    # The default converter in logging.Formatter uses time.localtime().
    # We override it to use time.gmtime() for UTC.
    converter = time.gmtime


def setup_logger(loger_level=logging.INFO):
    """
    Configures a logger to print to the console and a file.

    Format: LEVEL | YYYY-MM-DD HH:MM (UTC) | MODULE | MESSAGE

    - Development (running .py script): Logs to console and file.
    - Production (running .exe): Logs are disabled.
    """
    IS_EXECUTABLE = getattr(sys, "frozen", False)

    logger = logging.getLogger()
    if IS_EXECUTABLE:
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)

    else:
        logger.setLevel(loger_level)
        # Prevent adding duplicate handlers if this function is called more than once
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create a formatter with the specified UTC time format
        log_format = "%(levelname)-8s | %(asctime)s | %(module)-30s | %(message)s"
        utc_formatter = UTCFormatter(log_format, datefmt="%Y-%m-%d %H:%M")

        # --- Console Handler ---
        # This handler prints logs to the console (standard output)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(utc_formatter)
        logger.addHandler(console_handler)

        # --- File Handler ---
        # This handler writes logs to the 'rss_islandr.log' file
        # mode='w' will overwrite the log file each time the application starts
        file_handler = logging.FileHandler("rss_islandr.log", mode="w")
        file_handler.setFormatter(utc_formatter)
        logger.addHandler(file_handler)

    return logger
