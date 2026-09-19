import logging
import sys

import pytest

from rss_islandr.core import logger_config


@pytest.fixture
def clean_root_logger():
    """Give the root logger its handlers and level back after the test."""
    root = logging.getLogger()
    handlers, level = list(root.handlers), root.level
    yield root
    root.handlers[:] = handlers
    root.setLevel(level)


def remove_all_colors(messages):
    return [logger_config.remove_color_codes(message) for message in messages]


def test_color_codes_are_removed_from_log_messages():
    """
    Steps:
    1. Remove the color codes from a message that has the green and the reset code.

    Expected result:
    - Only the plain text remains.
    """
    message = f"{logger_config.GREEN}Finish: module.function{logger_config.RESET_COLOR}"

    assert logger_config.remove_color_codes(message) == "Finish: module.function"


def test_decorated_function_returns_its_result_and_logs_start_and_finish(caplog):
    """
    Steps:
    1. Decorate a function that adds two numbers.
    2. Call it with debug logging on.

    Expected result:
    - The result is unchanged and one "Start" and one "Finish" message are logged.
    """

    @logger_config.logger_decorator
    def add(a, b):
        return a + b

    with caplog.at_level(logging.DEBUG):
        assert add(1, 2) == 3

    messages = remove_all_colors(caplog.messages)
    assert any(message.startswith("Start :") for message in messages)
    assert any(message.startswith("Finish:") for message in messages)


def test_logger_writes_to_the_console_and_a_file_when_running_from_source(clean_root_logger, tmp_path, monkeypatch):
    """
    Steps:
    1. Run from a temporary folder as from source (not as the installed application).
    2. Set up the logger and write a message.

    Expected result:
    - There is a console handler and a file handler, and the file `rss_islandr.log` contains the message.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr(sys, "frozen", raising=False)

    logger = logger_config.setup_logger(logging.INFO)
    logger.info("a test message")
    for handler in logger.handlers:
        handler.flush()

    kinds = {type(handler) for handler in logger.handlers}
    assert logging.FileHandler in kinds and logging.StreamHandler in kinds
    assert "a test message" in (tmp_path / "rss_islandr.log").read_text(encoding="utf-8")


def test_logging_is_disabled_in_the_installed_application(clean_root_logger, tmp_path, monkeypatch):
    """
    Steps:
    1. Run as the installed application (frozen).
    2. Set up the logger.

    Expected result:
    - The logger has only a handler that discards messages and no log file is created.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    logger = logger_config.setup_logger(logging.INFO)

    assert any(isinstance(handler, logging.NullHandler) for handler in logger.handlers)
    assert not (tmp_path / "rss_islandr.log").exists()


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
