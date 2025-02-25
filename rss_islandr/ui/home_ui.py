import ttkbootstrap as tb
from core.config_parser import (
    ui_bg_color_1,
    ui_bg_color_2,
    ui_bg_color_3,
    ui_btn_bg_color_1,
    ui_btn_bg_color_2,
    ui_btn_font_color_1,
    ui_btn_font_color_2,
    ui_font_color_1,
    ui_font_color_2,
    ui_font_color_3,
    ui_font_size,
    ui_font_type,
    ui_title_font_color,
    ui_title_font_size,
    ui_title_font_type,
    ui_title_offset,
)
from core.datatypes import UISettings
from custom_themes import CustomThemes


class HomeUI:
    def __init__(self, parent_frame: tb.Frame, theme: str):
        self.parent_frame = parent_frame
        self.theme = theme

    def toggle_theme(self):
        # create ui_settings class by importing directly since they will change
        ui_settings = UISettings(
            ui_title_font_type,
            ui_title_font_size,
            ui_title_font_color,
            ui_title_offset,
            ui_bg_color_1,
            ui_bg_color_2,
            ui_bg_color_3,
            ui_font_type,
            ui_font_size,
            ui_font_color_1,
            ui_font_color_2,
            ui_font_color_3,
            ui_btn_bg_color_1,
            ui_btn_bg_color_2,
            ui_btn_font_color_1,
            ui_btn_font_color_2,
        )

        # Determine the new theme and update button text accordingly
        if self.theme == "darkly":  # If the current theme is dark, switch to light
            self.theme = "minty"
            self.toggle_button.config(text="Switch to Light Mode")
        else:  # If the current theme is light, switch to dark
            self.theme = "darkly"
            self.toggle_button.config(text="Switch to Dark Mode")

        # Reinitialize the style with the new theme
        self.__style = tb.Style(theme=self.theme)
        ct = CustomThemes(self.__style, ui_settings)
        ct()

        # self.ui_settings = ui_settings

    def __toggle_btn(self, frame: tb.Frame):
        self.toggle_button = tb.Button(frame, text="Switch to Light Mode", command=self.toggle_theme)
        self.toggle_button.pack(pady=20)

    def ui(self):
        self.__toggle_btn(self.parent_frame)
