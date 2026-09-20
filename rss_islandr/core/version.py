import sys
from importlib import metadata
from pathlib import Path

import tomllib

PACKAGE_NAME = "rss_islandr"
PYPROJECT_FILE = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"


def get_version() -> str:
    """
    Version of the application, e.g. '1.23.0'.

    When the application runs from the source code, the version is read from `pyproject.toml`, so a change of the
    version is visible at once. The installed application has no `pyproject.toml`; it reads the version from the
    package metadata that is added when the application is built (see `islandr.spec`).
    """
    if not getattr(sys, "frozen", False) and PYPROJECT_FILE.exists():
        with open(PYPROJECT_FILE, "rb") as pyproject_file:
            return tomllib.load(pyproject_file)["tool"]["poetry"]["version"]
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return "unknown"
