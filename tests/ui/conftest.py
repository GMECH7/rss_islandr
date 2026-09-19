import tkinter as tk

import pytest
import ttkbootstrap as tb

from rss_islandr.core.config_parser import settings
from rss_islandr.core.skin_reader import read_skin_details


@pytest.fixture(scope="session")
def root():
    """
    The one Tk window shared by all UI tests.

    ttkbootstrap keeps a reference to the first window it is created with, so a window that is created
    again after being destroyed by another test module would break.
    """
    ui_settings = read_skin_details(settings, "dark")
    try:
        window = tb.Window(themename=ui_settings.ui_ttkbootstrap_theme)  # always start with the dark theme
    except tk.TclError:
        pytest.skip("No display available")
    yield window
    window.destroy()
