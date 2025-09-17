import sys
import time

import pytest
import ttkbootstrap as tb

from rss_islandr.ui.main_app_ui import MainAppUI


@pytest.fixture
def app():
    root = tb.Window()
    main = MainAppUI(root)
    main.create_ui()
    yield main
    time.sleep(2)  # Allow time for cleanup
    root.destroy()


def test_ui_initialization(app):
    assert isinstance(app, MainAppUI)
    assert hasattr(app, "create_ui")


def test_site_info_button_click(app):
    app._nav_buttons_references["site_info"].invoke()


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
