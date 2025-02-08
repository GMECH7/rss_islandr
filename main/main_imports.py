import sys
from pathlib import Path

# Define MAIN_DIR as the directory containing the current file (__file__)
MAIN_DIR = Path(__file__).parent

# Define PROJECT_DIR as the parent directory of MAIN_DIR
PROJECT_DIR = MAIN_DIR.resolve().parent

# Define PACKAGE_DIR as the path to the 'rss_islandr' package inside PROJECT_DIR
PACKAGE_DIR = PROJECT_DIR / "rss_islandr"

# Add PROJECT_DIR to sys.path
sys.path.append(str(PROJECT_DIR))

import rss_islandr
