import os
import sys

import pytest

from rss_islandr.core import platform_setup


def test_input_method_is_disabled_on_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XMODIFIERS", raising=False)

    platform_setup.disable_input_method()

    assert os.environ["XMODIFIERS"] == "@im=none"


def test_value_set_by_the_desktop_is_replaced(monkeypatch):
    # Ubuntu sets XMODIFIERS=@im=ibus in every session
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XMODIFIERS", "@im=ibus")

    platform_setup.disable_input_method()

    assert os.environ["XMODIFIERS"] == "@im=none"


def test_input_method_can_be_kept(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XMODIFIERS", "@im=ibus")
    monkeypatch.setenv(platform_setup.KEEP_INPUT_METHOD_VARIABLE, "1")

    platform_setup.disable_input_method()

    assert os.environ["XMODIFIERS"] == "@im=ibus"


def test_nothing_changes_on_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("XMODIFIERS", raising=False)

    platform_setup.disable_input_method()

    assert "XMODIFIERS" not in os.environ


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
