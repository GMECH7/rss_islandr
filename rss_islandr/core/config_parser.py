# -*- coding: utf-8 -*-
import json
import os

MODULE_PATH = os.path.dirname(__file__)
SETTINGS_JSON_PATH = os.path.realpath(os.path.join(MODULE_PATH, "settings.json"))

################################################################################
######### Values read from settings.json (Changes allowed if necessary) ########
################################################################################
with open(SETTINGS_JSON_PATH, "r") as file_settings:
    settings = json.load(file_settings)

ui_bg_color_1: str = settings["UI"]["ui_bg_color_1"]
ui_bg_color_2: str = settings["UI"]["ui_bg_color_2"]
ui_font_color_1: str = settings["UI"]["ui_font_color_1"]
ui_font_color_2: str = settings["UI"]["ui_font_color_2"]
ui_heights: list[int] = settings["UI"]["ui_heights"]
ui_widths: list[int] = settings["UI"]["ui_widths"]
uis_canvas_names: dict[str, list["str"]] = settings["UI"]["uis_canvas_names"]
uis_frame_info: dict[str, dict[str, list[float]]] = settings["UI"]["uis_frame_info"]
