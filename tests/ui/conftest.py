import tkinter as tk

import pytest
import ttkbootstrap as tb

from rss_islandr.core.config_parser import settings
from rss_islandr.core.platform_setup import disable_input_method
from rss_islandr.core.skin_reader import read_skin_details
from rss_islandr.ui.main_app_ui import MainAppUI


@pytest.fixture(scope="session")
def root():
    """
    The one Tk window shared by all UI tests.

    ttkbootstrap keeps a reference to the first window it is created with, so a window that is created
    again after being destroyed by another test module would break.
    """
    disable_input_method()  # As in main(): the input method makes the window very slow to build
    ui_settings = read_skin_details(settings, "dark")
    try:
        window = tb.Window(themename=ui_settings.ui_ttkbootstrap_theme)  # always start with the dark theme
    except tk.TclError:
        pytest.skip("No display available")
    yield window
    window.destroy()


@pytest.fixture(scope="session")
def app(root):
    """The main app built like in main(), but without mainloop()."""
    main = MainAppUI(root)
    main.create_ui()
    root.update_idletasks()
    return main
