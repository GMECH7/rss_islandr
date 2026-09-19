"""
Message windows of the application.

All windows use the themed dialogs of ttkbootstrap, so they follow the dark/light theme of the application and look
the same everywhere. They open in the centre of the application window (of the screen when there is none). The
dialogs of the map page (`maps/js/dialogs.js`) use the same look. The functions take the title before the message,
like the functions of `tkinter.messagebox` that they replace.
"""

from ttkbootstrap.dialogs.dialogs import MessageDialog
from ttkbootstrap.icons import Icon


class CenteredMessageDialog(MessageDialog):
    """A themed message dialog that opens in the centre instead of the top left corner of its parent."""

    def _locate(self) -> None:
        toplevel = self._toplevel
        toplevel.update_idletasks()
        width, height = toplevel.winfo_reqwidth(), toplevel.winfo_reqheight()

        parent = self._parent if self._parent is not None else toplevel.master
        if parent is not None and parent.winfo_viewable():
            # winfo_rootx/y are the position of the content, winfo_x/y and the geometry of a window include the
            # border and title bar of the window manager: subtract them, so the content is centred
            border_x = parent.winfo_rootx() - parent.winfo_x()
            border_y = parent.winfo_rooty() - parent.winfo_y()
            centre_x = parent.winfo_rootx() + parent.winfo_width() // 2
            centre_y = parent.winfo_rooty() + parent.winfo_height() // 2
            x = centre_x - width // 2 - border_x
            y = centre_y - height // 2 - border_y
        else:
            centre_x = toplevel.winfo_screenwidth() // 2
            centre_y = toplevel.winfo_screenheight() // 2
            x, y = centre_x - width // 2, centre_y - height // 2

        self._placed = (max(x, 0), max(y, 0))
        self._wanted_centre = (centre_x, centre_y)
        toplevel.geometry(f"+{self._placed[0]}+{self._placed[1]}")
        # Some window managers add a title bar that cannot be measured before the window is shown
        toplevel.after(30, self._correct_position)

    def _correct_position(self) -> None:
        """Move the window when its content is not in the centre after it is shown (title bar of the window manager)."""
        toplevel = self._toplevel
        if not toplevel.winfo_exists():
            return
        actual_x = toplevel.winfo_rootx() + toplevel.winfo_width() // 2
        actual_y = toplevel.winfo_rooty() + toplevel.winfo_height() // 2
        shift_x, shift_y = self._wanted_centre[0] - actual_x, self._wanted_centre[1] - actual_y
        if abs(shift_x) > 2 or abs(shift_y) > 2:
            x, y = self._placed[0] + shift_x, self._placed[1] + shift_y
            self._placed = (max(x, 0), max(y, 0))
            toplevel.geometry(f"+{self._placed[0]}+{self._placed[1]}")


def _show(message: str, title: str, buttons: list[str], icon: str | None, parent) -> str | None:
    dialog = CenteredMessageDialog(message=message, title=title, parent=parent, buttons=buttons, icon=icon, localize=True)
    dialog.show()
    return dialog.result


def show_info(title: str, message: str, parent=None) -> None:
    """Information with an OK button."""
    _show(message, title, ["OK:primary"], Icon.info, parent)


def show_error(title: str, message: str, parent=None) -> None:
    """Error message with an OK button."""
    _show(message, title, ["OK:primary"], Icon.error, parent)


def ask_yes_no(title: str, message: str, parent=None) -> bool:
    """Question with the buttons No and Yes. Returns True for Yes."""
    return _show(message, title, ["No", "Yes"], None, parent) == "Yes"
