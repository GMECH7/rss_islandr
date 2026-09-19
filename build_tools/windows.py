import os
import shutil
import sys
from pathlib import Path

from rich.console import Console

from build_tools.common import APP_DIR, APP_NAME, DIST_DIR, BuildError, build_app, run
from build_tools.version import ROOT_DIR

#: File names without version, so that the link `.../releases/latest/download/<name>` always works
SETUP_NAME = "islandr-setup"
PORTABLE_NAME = "islandr-portable"

INNO_SCRIPT = ROOT_DIR / "installer" / "islandr.iss"
INNO_DEFAULT_PATHS = [
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Inno Setup 6" / "ISCC.exe",
]


def find_inno_setup() -> str:
    found = shutil.which("iscc") or next((str(path) for path in INNO_DEFAULT_PATHS if path.exists()), None)
    if not found:
        raise BuildError("Inno Setup 6 (ISCC.exe) was not found. Install it from https://jrsoftware.org/isinfo.php")
    return found


def inno_command(inno_compiler: str, version: str) -> list[str]:
    return [
        inno_compiler,
        f"/DAppVersion={version}",
        f"/DSourceDir={APP_DIR}",
        f"/DOutputDir={DIST_DIR}",
        f"/DOutputName={SETUP_NAME}",
        f"/DRootDir={ROOT_DIR}",
        str(INNO_SCRIPT),
    ]


def build_windows(console: Console) -> list[Path]:
    """Build the installer and the portable zip (only on Windows)."""
    if sys.platform != "win32":
        raise BuildError("--win can only be built on Windows")
    inno_compiler = find_inno_setup()
    version = build_app(console)

    console.rule("Creating the portable zip")
    portable_file = Path(shutil.make_archive(str(DIST_DIR / PORTABLE_NAME), "zip", DIST_DIR, APP_NAME))

    console.rule("Creating the installer")
    run(console, inno_command(inno_compiler, version))
    setup_file = DIST_DIR / f"{SETUP_NAME}.exe"
    if not setup_file.exists():
        raise BuildError(f"Inno Setup did not create {setup_file}")
    return [setup_file, portable_file]
