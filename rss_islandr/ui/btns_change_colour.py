import ttkbootstrap as tb

from rss_islandr.core.datatypes import UISettings
from rss_islandr.core.logger_config import logger_decorator


class BtnsChangeColour:
    """Change colour in buttons responsible for raising a Frame."""

    def __init__(self, ui_settings: UISettings, nav_buttons_references):
        self.__ui_settings = ui_settings
        self.__nav_buttons_references = nav_buttons_references

    def __reset_all_buttons(self) -> None:
        """Reset all navigation buttons to inactive style"""
        for btn in self.__nav_buttons_references.values():
            btn.configure(bootstyle=self.__ui_settings.ui_btn_bg_color_1)

    def __set_button_active(self, button_name: str) -> None:
        """Set the specified button to active style"""
        self.__nav_buttons_references[button_name].configure(bootstyle=self.__ui_settings.ui_btn_bg_color_2)

    @logger_decorator
    def show_page(self, page: tb.Frame, button_name: str) -> None:
        """Show the selected page and update button states"""
        self.__reset_all_buttons()
        self.__set_button_active(button_name)
        page.tkraise()
