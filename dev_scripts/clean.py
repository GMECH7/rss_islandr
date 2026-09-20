"""`poetry run clean`: remove the files that are created by building, testing and running the app."""

import argparse
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

ROOT_DIR = Path(__file__).resolve().parent.parent

#: Folders and files in the project folder that can be created again
GENERATED = ["dist", "build", ".cov_files", ".pytest_cache", "rss_islandr.log", "version_info.txt"]
#: Never searched for caches
SKIPPED_DIRS = {".venv", ".git", "node_modules"}


def find_generated(root: Path) -> list[Path]:
    """Generated files and folders in `root`, including the Python caches (not those of .venv)."""
    found = [root / name for name in GENERATED if (root / name).exists()]
    pending = [root]
    while pending:
        folder = pending.pop()
        for child in folder.iterdir():
            if not child.is_dir() or child.is_symlink() or child.name in SKIPPED_DIRS:
                continue
            if child.name == "__pycache__":
                found.append(child)
            else:
                pending.append(child)
    return sorted(found)


def size_of(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="clean", description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="only show what would be removed")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    console = Console()
    paths = find_generated(ROOT_DIR)
    if not paths:
        console.print("Nothing to clean.")
        return 0

    table = Table(title="Would be removed" if args.dry_run else "Removed")
    table.add_column("Path")
    table.add_column("Size", justify="right")
    total = 0
    for path in paths:
        size = size_of(path)
        total += size
        table.add_row(str(path.relative_to(ROOT_DIR)), f"{size / 1024 / 1024:.1f} MB")
        if not args.dry_run:
            remove(path)
    console.print(table)
    console.print(f"Total: {total / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
