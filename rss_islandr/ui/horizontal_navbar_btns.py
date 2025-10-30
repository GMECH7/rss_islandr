from tkinter import Menu

import ttkbootstrap as tb
from core.config_parser import settings
from core.datatypes import TkWidgets, UISettings
from core.skin_reader import read_skin_details
from custom_themes import CustomThemes
from io_btns import ExportExcelReportBtn, ExportPDFReportBtn, ExportScenarioBtn, ImportScenarioBtn, PopupImage

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable
from rss_islandr.core.logger_config import logger_decorator


class HorizontalNavbarBtns:
    """Implementation of buttons used in the horizontal navbar"""

    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        widgets_reconfigured: dict[TkWidgets, str],
    ):
        self.__theme_type = "dark"
        self.ui_settings = ui_settings
        self.__ui_inp_vars = ui_inp_vars
        self.__ui_calc_vars = ui_calc_vars
        self.__widgets_reconfigured = widgets_reconfigured

    @logger_decorator
    def toggle_theme(self):
        """Switch theme (dark-light)"""

        if self.__theme_type == "dark":  # If the current theme is dark, switch to light
            self.__theme_type = "light"
            self.toggle_button.config(text="Switch to Dark Mode")
            ui_settings_changed = read_skin_details(settings, self.__theme_type)
            theme_ttk = ui_settings_changed.ui_ttkbootstrap_theme
        else:  # If the current theme is light, switch to dark
            self.__theme_type = "dark"
            self.toggle_button.config(text="Switch to Light Mode")
            ui_settings_changed = read_skin_details(settings, self.__theme_type)
            theme_ttk = ui_settings_changed.ui_ttkbootstrap_theme

        self.__style = tb.Style(theme=theme_ttk)
        CustomThemes(self.__style, ui_settings_changed)()

        self.__reassign_values(ui_settings_changed)
        for widget, boot_style in self.__widgets_reconfigured.items():
            widget.configure(bootstyle=getattr(self.ui_settings, boot_style))

    def __reassign_values(self, ui_settings_changed: UISettings):
        """After changing skin values are reassigned"""
        for key, value in ui_settings_changed.__dict__.items():
            setattr(self.ui_settings, key, value)

    @logger_decorator
    def toggle_skin_btn(self, frame: tb.Frame):
        """Button used for switching between light and dark skin."""

        self.toggle_button = tb.Checkbutton(
            frame,
            text="Switch to Light Mode",
            style="round-toggle",
            command=self.toggle_theme,
        )

        self.toggle_button.grid()
        self.toggle_button.grid(row=0, column=23)

    @logger_decorator
    def file_menu_btn(self, frame: tb.Frame, **kwargs) -> None:
        """
        File menu. Import and Export options.
        """
        write_to_excel = ExportExcelReportBtn(self.__ui_inp_vars, self.__ui_calc_vars, **kwargs)
        write_to_pdf = ExportPDFReportBtn(self.__ui_inp_vars, self.__ui_calc_vars, **kwargs)
        write_to_json = ExportScenarioBtn(self.__ui_inp_vars, self.__ui_calc_vars, **kwargs)
        read_from_json = ImportScenarioBtn(self.__ui_inp_vars, self.__ui_calc_vars, **kwargs)

        menu_btn = tb.Menubutton(frame, text="File", style="Custom.Menubutton.TMenubutton")
        menu_btn.grid(row=0, column=0, sticky="w", padx=10)

        menu = Menu(menu_btn, tearoff=0)

        menu.add_command(label="Export Excel report", command=write_to_excel.on_btn_click)
        menu.add_command(label="Export PDF report", command=write_to_pdf.on_btn_click)
        menu.add_command(label="Export scenario", command=write_to_json.on_btn_click)
        menu.add_command(label="Import scenario", command=read_from_json.on_btn_click)
        menu_btn["menu"] = menu

    @logger_decorator
    def docs_menu_button(self, frame: tb.Frame) -> None:
        """
        Various documents displayed in popup menus.
        """
        popup_image = PopupImage(self.__ui_inp_vars, self.__ui_calc_vars)

        menu_btn = tb.Menubutton(frame, text="Documents", style="Custom.Menubutton.TMenubutton")
        menu_btn.grid(row=0, column=1, sticky="w")

        menu = Menu(menu_btn, tearoff=0)

        menu.add_command(label="Conceptual site model (CSM)", command=lambda: popup_image.on_btn_click(frame))
        menu_btn["menu"] = menu
