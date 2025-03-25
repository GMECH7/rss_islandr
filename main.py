import logging

import ttkbootstrap as tb

from rss_islandr.core.config_parser import (
    ICO_DIR,
    app_title,
    settings,
)
from rss_islandr.core.skin_reader import read_skin_details
from rss_islandr.ui import MainAppUI

logging.basicConfig(level=logging.INFO)


def main():
    ui_settings = read_skin_details(settings, "dark")
    theme = ui_settings.ui_ttkbootstrap_theme  # always start with the dark theme
    root = tb.Window(themename=theme)
    root.minsize(800, 800)
    root.title(app_title)
    root.iconbitmap(ICO_DIR)
    main = MainAppUI(root)
    main.create_ui()
    root.protocol("WM_DELETE_WINDOW", main.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
