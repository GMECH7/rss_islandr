import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from build_installer.common import BuildError, format_size


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="rss-build",
        description="Build the installer of RSS-ISLANDR. The version is `version` in pyproject.toml.",
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--win", action="store_true", help="Windows: installer and portable zip (run on Windows)")
    target.add_argument("--deb", action="store_true", help="Ubuntu/Debian package (run on Linux, or with --docker)")
    target.add_argument("--test-deb", action="store_true", help="test dist/*.deb in clean Ubuntu containers (Docker)")
    parser.add_argument("--docker", action="store_true", help="with --deb: build in the Ubuntu 24.04 container")
    args = parser.parse_args(argv)
    if args.docker and not args.deb:
        parser.error("--docker can only be used with --deb")
    return args


def show_results(console: Console, files: list[Path]) -> None:
    table = Table(title="Created files")
    table.add_column("File")
    table.add_column("Size", justify="right")
    for file in files:
        table.add_row(str(file), format_size(file))
    console.print(table)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    console = Console()
    try:
        if args.win:
            from build_installer.windows import build_windows

            show_results(console, build_windows(console))
        elif args.deb:
            from build_installer.debian import build_deb, build_deb_in_docker

            show_results(console, [build_deb_in_docker(console) if args.docker else build_deb(console)])
        elif args.test_deb:
            from build_installer.debian import build_version, deb_path, test_deb

            test_deb(console, deb_path(build_version()))
    except BuildError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
