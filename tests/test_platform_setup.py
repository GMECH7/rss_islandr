import os
import sys

import pytest

from rss_islandr.core import platform_setup


def test_input_method_is_disabled_on_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XMODIFIERS", raising=False)

    platform_setup.disable_input_method()

    assert os.environ["XMODIFIERS"] == "@im=none"


def test_setting_of_the_user_is_kept(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XMODIFIERS", "@im=fcitx")

    platform_setup.disable_input_method()

    assert os.environ["XMODIFIERS"] == "@im=fcitx"


def test_nothing_changes_on_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("XMODIFIERS", raising=False)

    platform_setup.disable_input_method()

    assert "XMODIFIERS" not in os.environ


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
