import argparse
import locale
import logging
import sys
import tkinter as tk

import ttkbootstrap as tb

from rss_islandr.core.config_parser import (
    ICO_DIR,
    ISLANDR_LOGO,
    app_title,
    settings,
)
from rss_islandr.core.logger_config import setup_logger
from rss_islandr.core.platform_setup import disable_input_method
from rss_islandr.core.skin_reader import read_skin_details
from rss_islandr.ui import MainAppUI

try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:  # The locale is not installed (e.g. minimal Linux systems/containers)
    pass

setup_logger(logging.INFO)


def set_window_icon(root: tb.Window) -> None:
    """Set the window icon. Tk on Windows takes a .ico file; on Linux/macOS it needs an image (PNG)."""
    try:
        if sys.platform == "win32":
            root.iconbitmap(ICO_DIR)
        else:
            root.iconphoto(True, tk.PhotoImage(file=ISLANDR_LOGO))
    except tk.TclError:
        logging.warning("Could not set the window icon.")


def show_loading(root: tb.Window) -> tb.Frame:
    """Show a message while the main window is being built (it can take a few seconds on slow systems)."""
    frame = tb.Frame(root)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    tb.Label(frame, text=f"Loading {app_title}...", font=("calibri", 18)).place(relx=0.5, rely=0.5, anchor="center")
    root.update()
    return frame


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="islandr", description="Risk Screening System (RSS) - ISLANDR")
    parser.add_argument("--self-test", action="store_true", help="check the installation and exit (0 = OK)")
    parser.add_argument("--self-test-report", metavar="FILE", help="also write the result of --self-test to FILE")
    parser.add_argument("--map-process", action="store_true", help=argparse.SUPPRESS)  # used internally (Linux/macOS)
    return parser.parse_args(argv)


def main():
    disable_input_method()  # Must happen before the first Tk window is created
    ui_settings = read_skin_details(settings, "dark")
    theme = ui_settings.ui_ttkbootstrap_theme  # always start with the dark theme
    root = tb.Window(themename=theme)
    root.minsize(800, 800)
    root.title(app_title)
    set_window_icon(root)
    loading_frame = show_loading(root)
    main = MainAppUI(root)
    main.create_ui()
    loading_frame.destroy()
    root.protocol("WM_DELETE_WINDOW", main.on_closing)
    root.mainloop()


if __name__ == "__main__":
    args = parse_args()
    if args.map_process:
        from rss_islandr.ui.map_ui import _run_map_process

        _run_map_process()
    elif args.self_test:
        from rss_islandr.self_test import run_self_test

        sys.exit(run_self_test(args.self_test_report))
    else:
        main()
