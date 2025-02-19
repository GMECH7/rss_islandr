# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

from .datatypes import UISettings

# Define the base directory
if getattr(sys, "frozen", False):  # noqa: SIM108
    # Running in a PyInstaller bundle
    PROJECT_DIR = Path(sys._MEIPASS)
else:
    MODULE_DIR = Path(__file__).parent
    PROJECT_DIR = MODULE_DIR.resolve().parent
    PACKAGE_DIR = PROJECT_DIR / "rss_islandr"

# Access files in the 'static' folder
STATIC_DIR = PROJECT_DIR / "static"
ICO_DIR = STATIC_DIR / "islandr.ico"
MAP_DIR = STATIC_DIR / "map.html"
GEOLOGY_LEGEND_DIR = STATIC_DIR / "geology_legend.png"
HYDRO_LEGEND_DIR = STATIC_DIR / "hydro_legend.png"

DATA_DIR = PROJECT_DIR / "data"

SETTINGS_JSON_DIR = PROJECT_DIR / "core" / "settings.json"
RECEPTOR_FACTORS_JSON_DIR = DATA_DIR / "receptor_factors.json"
RISK_FACTORS_JSON_DIR = DATA_DIR / "risk_factors.json"
DROPDOWN_LISTS_JSON_DIR = DATA_DIR / "dropdown_lists.json"

with open(SETTINGS_JSON_DIR, "r", encoding="utf-8") as file_settings:
    settings = json.load(file_settings)

# hardcoded
skin_color = "dark_skin"

ui_title_font_type: str = settings["UI"]["ui_title_font_type"]
ui_title_font_size: int = settings["UI"]["ui_title_font_size"]
ui_title_font_color: str = settings["UI"]["ui_title_font_color"]
ui_title_offset: float = settings["UI"]["ui_title_offset"]

ui_bg_color_1: str = settings["UI"][skin_color]["ui_bg_color_1"]
ui_bg_color_2: str = settings["UI"][skin_color]["ui_bg_color_2"]

ui_font_type: str = settings["UI"]["font_type"]
ui_font_size: int = settings["UI"]["font_size"]
ui_font_color_1: str = settings["UI"][skin_color]["ui_font_color_1"]
ui_font_color_2: str = settings["UI"][skin_color]["ui_font_color_2"]

ui_btn_bg_color_1: str = settings["UI"][skin_color]["ui_btn_bg_color_1"]
ui_btn_bg_color_2: str = settings["UI"][skin_color]["ui_btn_bg_color_2"]

ui_btn_font_color_1: str = settings["UI"][skin_color]["ui_btn_font_color_1"]
ui_btn_font_color_2: str = settings["UI"][skin_color]["ui_btn_font_color_2"]

ui_heights: list[int] = settings["UI"]["ui_heights"]
ui_widths: list[int] = settings["UI"]["ui_widths"]

uis_canvas_names: dict[str, list["str"]] = settings["UI"]["uis_canvas_names"]
uis_frame_info: dict[str, dict[str, dict]] = settings["UI"]["uis_frame_info"]


risk_limits_color: dict[str, list[float]] = settings["risk_limits_color"]


ui_settings = UISettings(
    ui_title_font_type,
    ui_title_font_size,
    ui_title_font_color,
    ui_title_offset,
    ui_bg_color_1,
    ui_bg_color_2,
    ui_font_type,
    ui_font_size,
    ui_font_color_1,
    ui_font_color_2,
    ui_btn_bg_color_1,
    ui_btn_bg_color_2,
    ui_btn_font_color_1,
    ui_btn_font_color_2,
)
