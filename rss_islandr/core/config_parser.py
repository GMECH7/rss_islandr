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
TEMPLATES_DIR = PROJECT_DIR / "templates"
REPORTS_DIR = PROJECT_DIR / "reports"

SETTINGS_JSON_DIR = PROJECT_DIR / "core" / "settings.json"
RECEPTOR_FACTORS_JSON_DIR = DATA_DIR / "receptor_factors.json"
RISK_FACTORS_JSON_DIR = DATA_DIR / "risk_factors.json"
DROPDOWN_LISTS_JSON_DIR = DATA_DIR / "dropdown_lists.json"
XLSX_TEMPLATE_FILE = TEMPLATES_DIR / "report_template.xlsx"
XLSX_TEMPLATE_FILE_COPY = TEMPLATES_DIR / "report_template__COPY.xlsx"
with open(SETTINGS_JSON_DIR, "r", encoding="utf-8") as file_settings:
    settings = json.load(file_settings)

skin_color = "dark_skin"

source_keys: list[str] = settings["source_keys"]
pathway_keys: list[str] = settings["pathway_keys"]
risk_limits_color: dict[str, list[float]] = settings["risk_limits_color"]

#: UI related settings
app_title: str = settings["UI"]["app_title"]

ui_heights: list[int] = settings["UI"]["ui_heights"]
ui_widths: list[int] = settings["UI"]["ui_widths"]

uis_frame_geometry: dict[str, dict] = settings["UI"]["uis_frame_geometry"]
