"""`poetry run islandr`: start the app from the source code (the same as `python main.py`)."""

import sys

from rss_islandr.app import run


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
