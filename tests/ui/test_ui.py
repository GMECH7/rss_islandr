import sys

import pytest

from rss_islandr.ui.main_app_ui import MainAppUI


def test_ui_initialization(app):
    assert isinstance(app, MainAppUI)
    assert hasattr(app, "create_ui")


def test_home_page(app):
    app._nav_buttons_references["home"].invoke()
    app.root.update()
    assert app._home_page.winfo_viewable() == 1


def test_click_site_info(app):
    app._nav_buttons_references["site_info"].invoke()
    app.root.update()
    assert app._site_info_page.winfo_viewable() == 1


def test_click_on_site_on_site(app):
    app._nav_buttons_references["on_site_on_site"].invoke()
    app.root.update()
    assert app._on_site_on_site_page.winfo_viewable() == 1


def test_click_on_site_off_site(app):
    app._nav_buttons_references["on_site_off_site"].invoke()
    app.root.update()
    assert app._on_site_off_site_page.winfo_viewable() == 1


def test_click_off_site_on_site(app):
    app._nav_buttons_references["off_site_on_site"].invoke()
    app.root.update()
    assert app._off_site_on_site_page.winfo_viewable() == 1


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
