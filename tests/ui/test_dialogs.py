import sys

import pytest

from rss_islandr.ui import dialogs


class FakeMessagebox:
    """Records the calls of the ttkbootstrap dialogs and answers with a prepared value."""

    def __init__(self, answer=None):
        self.answer = answer
        self.calls = []

    def show_info(self, *args, **kwargs):
        self.calls.append(("show_info", args, kwargs))

    def show_error(self, *args, **kwargs):
        self.calls.append(("show_error", args, kwargs))

    def yesno(self, *args, **kwargs):
        self.calls.append(("yesno", args, kwargs))
        return self.answer


def test_information_window_shows_title_and_message(monkeypatch):
    """
    Steps:
    1. Show an information window with the title "About" and the message "Version 1".

    Expected result:
    - The themed dialog is opened once with the message first and then the title (the order of ttkbootstrap).
    """
    fake = FakeMessagebox()
    monkeypatch.setattr(dialogs, "Messagebox", fake)

    dialogs.show_info("About", "Version 1")

    assert fake.calls == [("show_info", ("Version 1", "About"), {"parent": None})]


def test_error_window_shows_title_and_message(monkeypatch):
    """
    Steps:
    1. Show an error window with the title "Error" and the message "Something failed".

    Expected result:
    - The themed error dialog is opened once with the message and the title.
    """
    fake = FakeMessagebox()
    monkeypatch.setattr(dialogs, "Messagebox", fake)

    dialogs.show_error("Error", "Something failed")

    assert fake.calls == [("show_error", ("Something failed", "Error"), {"parent": None})]


@pytest.mark.parametrize(("answer", "expected"), [("Yes", True), ("No", False), (None, False)])
def test_question_returns_true_only_for_yes(monkeypatch, answer, expected):
    """
    Steps:
    1. Ask a yes/no question and answer "Yes", "No" or close the window without an answer (one test run for each).

    Expected result:
    - The result is True only for "Yes".
    """
    monkeypatch.setattr(dialogs, "Messagebox", FakeMessagebox(answer))

    assert dialogs.ask_yes_no("Confirmation", "Are you sure?") is expected


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
