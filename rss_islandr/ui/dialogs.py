"""
Message windows of the application.

All windows use the themed dialogs of ttkbootstrap, so they follow the dark/light theme of the application and look
the same everywhere. The dialogs of the map page (`maps/js/dialogs.js`) use the same look. The functions take the
title before the message, like the functions of `tkinter.messagebox` that they replace.
"""

from ttkbootstrap.dialogs import Messagebox


def show_info(title: str, message: str, parent=None) -> None:
    """Information with an OK button."""
    Messagebox.show_info(message, title, parent=parent)


def show_error(title: str, message: str, parent=None) -> None:
    """Error message with an OK button."""
    Messagebox.show_error(message, title, parent=parent)


def ask_yes_no(title: str, message: str, parent=None) -> bool:
    """Question with the buttons No and Yes. Returns True for Yes."""
    return Messagebox.yesno(message, title, parent=parent) == "Yes"
