import sys
import tkinter as tk

import pytest

from rss_islandr import app as app_module


def test_loading_message_is_shown_and_can_be_removed(root):
    """
    Steps:
    1. Show the loading message on the window.
    2. Remove it.

    Expected result:
    - The message frame covers the whole window and contains the text "Loading". After it is destroyed it is
      no longer a child of the window.
    """
    frame = app_module.show_loading(root)

    texts = [child.cget("text") for child in frame.winfo_children()]
    assert any("Loading" in text for text in texts)
    assert frame.place_info()["relwidth"] == "1"
    assert frame.winfo_exists()

    frame.destroy()

    assert frame not in root.winfo_children()


def test_window_icon_is_set_without_error(root):
    """
    Steps:
    1. Set the window icon.

    Expected result:
    - No error is raised (an .ico file on Windows, the PNG logo on other systems).
    """
    app_module.set_window_icon(root)


def test_failing_icon_is_only_logged(root, monkeypatch, caplog):
    """
    Steps:
    1. Make the window refuse the icon.
    2. Set the window icon.

    Expected result:
    - No error is raised and a warning is logged.
    """

    def refuse(*args, **kwargs):
        raise tk.TclError("not supported")

    monkeypatch.setattr(root, "iconphoto", refuse)
    monkeypatch.setattr(root, "iconbitmap", refuse)

    app_module.set_window_icon(root)

    assert "Could not set the window icon" in caplog.text


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
