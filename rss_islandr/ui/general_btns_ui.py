from tkinter import Menu

import ttkbootstrap as tb
from core.config_parser import settings
from core.datatypes import UISettings
from core.skin_reader import read_skin_details
from custom_themes import CustomThemes
from io_btns import ExportExcelReportBtn, ExportScenarioBtn, ImportScenarioBtn, PopupImage


class GeneralBtnsUI:
    """Implementation of buttons that may be used anywhere in the app."""

    def __init__(self, ui_settings: UISettings, ui_inp_vars, ui_calc_vars, widgets_reconfigured: dict[tb.Frame, str]):
        self.__theme_type = "dark"
        self.ui_settings = ui_settings
        self.__ui_inp_vars = ui_inp_vars
        self.__ui_calc_vars = ui_calc_vars
        self.__widgets_reconfigured = widgets_reconfigured

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

    def toggle_skin_btn(self, frame: tb.Frame):
        """Button used for switching between light and dark skin."""

        self.toggle_button = tb.Checkbutton(
            frame,
            text="Switch to Light Mode",
            style="round-toggle",
            command=self.toggle_theme,
        )

        self.toggle_button.grid()

        self.toggle_button.grid(row=0, column=11)

    def file_menu_btn(self, frame: tb.Frame):
        """
        File menu. Import and Export options.
        """
        write_to_excel = ExportExcelReportBtn(self.__ui_inp_vars, self.__ui_calc_vars)
        write_to_json = ExportScenarioBtn(self.__ui_inp_vars, self.__ui_calc_vars)
        read_from_json = ImportScenarioBtn(self.__ui_inp_vars, self.__ui_calc_vars)

        menu_btn = tb.Menubutton(frame, text="File", style="Custom.Menubutton.TMenubutton")
        menu_btn.grid(row=0, column=0, sticky="nsw")

        menu = Menu(menu_btn, tearoff=0)

        menu.add_command(label="Export report", command=write_to_excel.on_btn_click)
        menu.add_command(label="Export scenario", command=write_to_json.on_btn_click)
        menu.add_command(label="Import scenario", command=read_from_json.on_btn_click)
        menu_btn["menu"] = menu

    def docs_menu_button(self, frame: tb.Frame):
        """
        Various documents displayed in popup menus.
        """
        popup_image = PopupImage(self.__ui_inp_vars, self.__ui_calc_vars)
        menu_btn = tb.Menubutton(frame, text="Documents", style="Custom.Menubutton.TMenubutton")
        menu_btn.grid(row=0, column=1, sticky="nsw")

        menu = Menu(menu_btn, tearoff=0)

        menu.add_command(label="Conceptual site model (CSM)", command=lambda: popup_image.on_btn_click(frame))

        menu_btn["menu"] = menu
