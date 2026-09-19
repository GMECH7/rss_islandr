import json
import sys
from pathlib import Path

# Define the base directory
if getattr(sys, "frozen", False):
    # Running in a PyInstaller bundle
    PROJECT_DIR = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    MODULE_DIR = Path(__file__).parent
    PROJECT_DIR = MODULE_DIR.resolve().parent
    PACKAGE_DIR = PROJECT_DIR / "rss_islandr"

# Access files in the 'static' folder
STATIC_DIR = PROJECT_DIR / "static"
MAPS_DIR = PROJECT_DIR / "maps"
ICO_DIR = STATIC_DIR / "islandr.ico"
MAP_DIR = MAPS_DIR / "index.html"
GEOLOGY_LEGEND_DIR = STATIC_DIR / "geology_legend.png"
HYDRO_LEGEND_DIR = STATIC_DIR / "hydro_legend.png"
ISLANDR_LOGO = STATIC_DIR / "islandr_logo.png"

DATA_DIR = PROJECT_DIR / "data"
TEMPLATES_DIR = PROJECT_DIR / "templates"
REPORTS_DIR = PROJECT_DIR / "reports"

SETTINGS_JSON_DIR = DATA_DIR / "settings.json"
RECEPTOR_FACTORS_JSON_DIR = DATA_DIR / "receptor_factors.json"
RISK_FACTORS_JSON_DIR = DATA_DIR / "risk_factors.json"
DROPDOWN_LISTS_JSON_DIR = DATA_DIR / "dropdown_lists.json"
XLSX_TEMPLATE_FILE = TEMPLATES_DIR / "report_template.xlsx"
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

font_size_pdf_1 = settings["PDF_report"]["font_size_pdf_1"]
font_size_pdf_2 = settings["PDF_report"]["font_size_pdf_2"]
font_size_pdf_3 = settings["PDF_report"]["font_size_pdf_3"]
