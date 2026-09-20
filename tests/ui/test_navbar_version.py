import sys

import pytest

from rss_islandr.core.version import get_version
from rss_islandr.ui import dialogs


def _version_menu_buttons(widget):
    for child in widget.winfo_children():
        if child.winfo_class() == "TMenubutton" and child.cget("text") == "Version":
            yield child
        yield from _version_menu_buttons(child)


def test_navbar_has_a_version_menu_next_to_the_documents_menu(app):
    """
    Steps:
    1. Look at the navigation bars of the main window (every page has one).
    2. Open the menu of the "Version" button.

    Expected result:
    - Every navigation bar has a "Version" menu button in the same row as the File and Documents menus, to the
      right of the Documents menu.
    - Its menu has one entry with the text "Version <version of the application>".
    """
    buttons = list(_version_menu_buttons(app.root))

    assert len(buttons) >= 1
    for button in buttons:
        grid = button.grid_info()
        assert (grid["row"], grid["column"]) == (0, 2)
        menu = button.nametowidget(button.cget("menu"))
        assert menu.index("end") == 0
        assert menu.entrycget(0, "label") == f"Version {get_version()}"


def test_version_entry_opens_a_window_with_the_version(app, monkeypatch):
    """
    Steps:
    1. Replace the message window by a recorder.
    2. Select the entry of the "Version" menu.

    Expected result:
    - A window "About RSS-ISLANDR" is shown with the application name and the version.
    """
    shown = []
    monkeypatch.setattr(dialogs, "show_info", lambda *args, **kwargs: shown.append(args))
    button = next(_version_menu_buttons(app.root))

    button.nametowidget(button.cget("menu")).invoke(0)

    assert shown == [("About RSS-ISLANDR", f"RSS-ISLANDR\nVersion {get_version()}")]


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
