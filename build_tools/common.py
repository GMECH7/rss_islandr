import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console

from build_tools.version import ROOT_DIR, read_version, write_version_info

DIST_DIR = ROOT_DIR / "dist"
APP_DIR = DIST_DIR / "islandr"  # Output of PyInstaller (one-folder build)
APP_NAME = "islandr"


class BuildError(Exception):
    pass


def run(console: Console, command: list, *, cwd: Path = ROOT_DIR, env: dict | None = None) -> None:
    """Run a command, show its output, and raise a BuildError if it fails."""
    command = [str(part) for part in command]
    console.print(f"[dim]$ {' '.join(command)}[/dim]")
    result = subprocess.run(command, cwd=cwd, env={**os.environ, **(env or {})})
    if result.returncode != 0:
        raise BuildError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")


def with_display(command: list) -> list:
    """The self-test opens a window: on Linux without a display (e.g. in a container) run it in a virtual one."""
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        return ["xvfb-run", "-a", *command]
    return command


def build_app(console: Console) -> str:
    """Build the one-folder application with PyInstaller and check it with the self-test. Returns the version."""
    version = read_version()
    console.rule(f"Building the application, version {version}")
    write_version_info(version)

    shutil.rmtree(APP_DIR, ignore_errors=True)
    run(console, [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "islandr.spec"])

    executable = APP_DIR / (f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME)
    if not executable.exists():
        raise BuildError(f"PyInstaller did not create {executable}")

    console.rule("Self-test of the built application")
    with tempfile.TemporaryDirectory() as tmp_dir:
        report_file = Path(tmp_dir) / "self_test.txt"
        result = subprocess.run(
            with_display([str(executable), "--self-test", "--self-test-report", str(report_file)]), cwd=ROOT_DIR
        )
        # The windowed Windows executable has no console: show the report file
        if report_file.exists():
            console.print(report_file.read_text(encoding="utf-8"))
        if result.returncode != 0:
            raise BuildError("The self-test of the built application failed")
    return version


def format_size(path: Path) -> str:
    size = path.stat().st_size
    return f"{size / 1024 / 1024:.0f} MB"
