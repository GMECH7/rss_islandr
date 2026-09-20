import sys
from types import SimpleNamespace
from typing import ClassVar

import pytest

from rss_islandr.ui import dialogs


class FakeDialog:
    """Records the dialogs that are created and shown, and answers with a prepared value."""

    created: ClassVar[list] = []
    answer = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.shown = False
        FakeDialog.created.append(self)

    def show(self):
        self.shown = True

    @property
    def result(self):
        return FakeDialog.answer


@pytest.fixture
def fake_dialog(monkeypatch):
    FakeDialog.created, FakeDialog.answer = [], None
    monkeypatch.setattr(dialogs, "CenteredMessageDialog", FakeDialog)
    return FakeDialog


def test_information_window_shows_title_and_message(fake_dialog):
    """
    Steps:
    1. Show an information window with the title "About" and the message "Version 1".

    Expected result:
    - One dialog with an OK button and the information icon is created and shown, with that title and message.
    """
    dialogs.show_info("About", "Version 1")

    (dialog,) = fake_dialog.created
    assert dialog.shown
    assert (dialog.kwargs["title"], dialog.kwargs["message"]) == ("About", "Version 1")
    assert dialog.kwargs["buttons"] == ["OK:primary"]
    assert dialog.kwargs["icon"] == dialogs.Icon.info


def test_error_window_shows_title_and_message(fake_dialog):
    """
    Steps:
    1. Show an error window with the title "Error" and the message "Something failed".

    Expected result:
    - One dialog with an OK button and the error icon is created and shown, with that title and message.
    """
    dialogs.show_error("Error", "Something failed")

    (dialog,) = fake_dialog.created
    assert dialog.shown
    assert (dialog.kwargs["title"], dialog.kwargs["message"]) == ("Error", "Something failed")
    assert dialog.kwargs["icon"] == dialogs.Icon.error


@pytest.mark.parametrize(("answer", "expected"), [("Yes", True), ("No", False), (None, False)])
def test_question_returns_true_only_for_yes(fake_dialog, answer, expected):
    """
    Steps:
    1. Ask a yes/no question and answer "Yes", "No" or close the window without an answer (one test run for each).

    Expected result:
    - The dialog has the buttons "No" and "Yes". The result is True only for "Yes".
    """
    fake_dialog.answer = answer

    assert dialogs.ask_yes_no("Confirmation", "Are you sure?") is expected
    assert fake_dialog.created[0].kwargs["buttons"] == ["No", "Yes"]


def _dialog_at(parent, size=(400, 200), screen=(1920, 1080)):
    """A dialog with a fake toplevel, to test where it is placed. Returns the dialog and the positions it is given."""
    placed, scheduled = [], []
    toplevel = SimpleNamespace(
        master=parent,
        update_idletasks=lambda: None,
        after=lambda milliseconds, function: scheduled.append(function),
        winfo_exists=lambda: True,
        winfo_reqwidth=lambda: size[0],
        winfo_reqheight=lambda: size[1],
        winfo_screenwidth=lambda: screen[0],
        winfo_screenheight=lambda: screen[1],
        geometry=placed.append,
    )
    dialog = dialogs.CenteredMessageDialog.__new__(dialogs.CenteredMessageDialog)
    dialog._toplevel, dialog._parent = toplevel, parent
    dialog.scheduled = scheduled
    return dialog, placed


def _window(x, y, width, height, viewable=True, border=(0, 0)):
    """A fake window whose content is at (x, y). `border` is the size of its border and title bar."""
    return SimpleNamespace(
        winfo_viewable=lambda: viewable,
        winfo_rootx=lambda: x,
        winfo_rooty=lambda: y,
        winfo_x=lambda: x - border[0],
        winfo_y=lambda: y - border[1],
        winfo_width=lambda: width,
        winfo_height=lambda: height,
    )


def test_dialog_opens_in_the_centre_of_the_application_window():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels over an application window at (100, 100) that is 1000 x 800 pixels.

    Expected result:
    - The dialog is placed at (400, 400), in the centre of the window.
    """
    dialog, placed = _dialog_at(_window(100, 100, 1000, 800))

    dialog._locate()

    assert placed == ["+400+400"]


def test_title_bar_of_the_window_manager_is_taken_into_account():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels over a window whose content is at (100, 100), is 1000 x 800 pixels and has
       a title bar of 37 pixels.

    Expected result:
    - The dialog is placed 37 pixels higher than the centre, at (400, 363), because its own title bar is added by
      the window manager. This puts its content in the centre.
    """
    dialog, placed = _dialog_at(_window(100, 100, 1000, 800, border=(0, 37)))

    dialog._locate()

    assert placed == ["+400+363"]


def test_dialog_opens_in_the_centre_of_the_screen_without_a_visible_window():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels when the application window is not visible, on a 1920 x 1080 screen.

    Expected result:
    - The dialog is placed at (760, 440), in the centre of the screen.
    """
    dialog, placed = _dialog_at(_window(0, 0, 10, 10, viewable=False))

    dialog._locate()

    assert placed == ["+760+440"]


def test_dialog_larger_than_its_window_stays_on_the_screen():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels over a small application window at (0, 0) that is 100 x 50 pixels.

    Expected result:
    - The position is not negative: the dialog is placed at (0, 0).
    """
    dialog, placed = _dialog_at(_window(0, 0, 100, 50))

    dialog._locate()

    assert placed == ["+0+0"]


def test_position_is_corrected_when_the_window_manager_adds_a_title_bar():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels over a window at (100, 100) that is 1000 x 800 pixels.
    2. Let the window manager show it 37 pixels too low (its content starts at y = 437 instead of 400).
    3. Run the correction that is scheduled after the dialog is shown.

    Expected result:
    - The dialog is moved up by 37 pixels: from (400, 400) to (400, 363).
    """
    dialog, placed = _dialog_at(_window(100, 100, 1000, 800))
    dialog._locate()
    toplevel = dialog._toplevel
    toplevel.winfo_rootx = lambda: 400
    toplevel.winfo_rooty = lambda: 437
    toplevel.winfo_width = lambda: 400
    toplevel.winfo_height = lambda: 200

    dialog.scheduled[0]()

    assert placed == ["+400+400", "+400+363"]


def test_position_is_kept_when_the_dialog_is_already_in_the_centre():
    """
    Steps:
    1. Place a dialog of 400 x 200 pixels over a window at (100, 100) that is 1000 x 800 pixels.
    2. Let the window manager show it exactly where requested.
    3. Run the correction that is scheduled after the dialog is shown.

    Expected result:
    - The dialog is not moved again.
    """
    dialog, placed = _dialog_at(_window(100, 100, 1000, 800))
    dialog._locate()
    toplevel = dialog._toplevel
    toplevel.winfo_rootx = lambda: 400
    toplevel.winfo_rooty = lambda: 400
    toplevel.winfo_width = lambda: 400
    toplevel.winfo_height = lambda: 200

    dialog.scheduled[0]()

    assert placed == ["+400+400"]


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
