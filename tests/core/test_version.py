import sys
from importlib import metadata

import pytest
import tomllib

from rss_islandr.core import version


def _pyproject_version():
    with open(version.PYPROJECT_FILE, "rb") as pyproject_file:
        return tomllib.load(pyproject_file)["tool"]["poetry"]["version"]


def test_version_is_read_from_pyproject_when_running_from_source():
    """
    Steps:
    1. Ask for the version of the application when running from the source code.

    Expected result:
    - It is the `version` of pyproject.toml, in the form X.Y.Z.
    """
    assert version.get_version() == _pyproject_version()
    assert len(version.get_version().split(".")) == 3


def test_installed_application_reads_the_package_metadata(monkeypatch):
    """
    Steps:
    1. Pretend to run as the installed application (frozen), which has no pyproject.toml.
    2. Make the package metadata return the version "9.8.7".
    3. Ask for the version.

    Expected result:
    - The version is "9.8.7".
    """
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(version.metadata, "version", lambda name: "9.8.7")

    assert version.get_version() == "9.8.7"


def test_version_is_unknown_without_pyproject_and_metadata(monkeypatch, tmp_path):
    """
    Steps:
    1. Point the version to a folder without pyproject.toml.
    2. Make the package metadata unavailable.
    3. Ask for the version.

    Expected result:
    - The version is "unknown" and no error is raised.
    """

    def missing(name):
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(version, "PYPROJECT_FILE", tmp_path / "pyproject.toml")
    monkeypatch.setattr(version.metadata, "version", missing)

    assert version.get_version() == "unknown"


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
