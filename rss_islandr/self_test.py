"""
Self-test of the installed application (``islandr --self-test``).

It checks that everything the app needs at run time is present and loads (data files, templates, maps,
the web engine used by the map viewer) and that the main window can be built. It is used to test the
built executables and installers without clicking through the app.
"""

import sys
from pathlib import Path
from typing import Callable

from rss_islandr.core import config_parser as cfg

REQUIRED_FILES: dict[str, Path] = {
    "settings": cfg.SETTINGS_JSON_DIR,
    "risk factors": cfg.RISK_FACTORS_JSON_DIR,
    "receptor factors": cfg.RECEPTOR_FACTORS_JSON_DIR,
    "dropdown lists": cfg.DROPDOWN_LISTS_JSON_DIR,
    "Excel template": cfg.XLSX_TEMPLATE_FILE,
    "map page": cfg.MAP_DIR,
    "map script": cfg.MAPS_DIR / "js" / "script.js",
    "map config": cfg.MAPS_DIR / "js" / "config.js",
    "logo": cfg.ISLANDR_LOGO,
    "icon": cfg.ICO_DIR,
    "risk image": cfg.STATIC_DIR / "csm.png",
}


def check_files() -> None:
    missing = [f"{name} ({path})" for name, path in REQUIRED_FILES.items() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing files: " + ", ".join(missing))


def check_risk_calculation() -> None:
    from rss_islandr.assessment import risk_calc

    assert risk_calc([0.5, 1.0, 0.5]) == 0.25


def check_excel_template() -> None:
    from openpyxl import load_workbook

    assert len(load_workbook(cfg.XLSX_TEMPLATE_FILE).worksheets) == 5


def check_web_engine() -> None:
    """The map viewer needs a web engine: WebView2/.NET on Windows, Qt WebEngine elsewhere."""
    if sys.platform == "win32":
        import clr  # noqa: F401  (pythonnet)
        import webview  # noqa: F401
    else:
        from qtpy import QtWebEngineWidgets  # noqa: F401


def check_main_window() -> None:
    import ttkbootstrap as tb

    from rss_islandr.core.skin_reader import read_skin_details
    from rss_islandr.ui import MainAppUI

    ui_settings = read_skin_details(cfg.settings, "dark")
    root = tb.Window(themename=ui_settings.ui_ttkbootstrap_theme)
    try:
        MainAppUI(root).create_ui()
        root.update()
    finally:
        root.destroy()


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("data and static files", check_files),
    ("risk calculation", check_risk_calculation),
    ("Excel template", check_excel_template),
    ("web engine of the map viewer", check_web_engine),
    ("main window", check_main_window),
]


def run_self_test(report_file: str | None = None) -> int:
    """
    Run all checks.

    Parameters
    ----------
    report_file : str | None
        If given, the result is also written to this file. Needed for the Windows executable, which has no console.

    Returns
    -------
    int
        Exit code: 0 if all checks passed, 1 otherwise.
    """
    lines = []
    failed = False
    for name, check in CHECKS:
        try:
            check()
            lines.append(f"OK    {name}")
        except Exception as e:
            failed = True
            lines.append(f"FAIL  {name}: {type(e).__name__}: {e}")
    lines.append("Self-test FAILED" if failed else "Self-test passed")

    report = "\n".join(lines)
    if sys.stdout is not None:  # No console in the windowed Windows executable
        print(report)
    if report_file:
        Path(report_file).write_text(report + "\n", encoding="utf-8")

    return 1 if failed else 0
