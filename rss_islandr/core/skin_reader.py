from .datatypes import UISettings


def read_skin_details(settings, skin_type: str) -> UISettings:
    ui_title_font_type: str = settings["UI"]["ui_title_font_type"]
    ui_title_font_size: int = settings["UI"]["ui_title_font_size"]
    ui_title_font_color: str = settings["UI"]["ui_title_font_color"]
    ui_title_offset: float = settings["UI"]["ui_title_offset"]

    ui_ttkbootstrap_theme: str = settings["UI"][skin_type]["ui_ttkbootstrap_theme"]
    ui_bg_color_1: str = settings["UI"][skin_type]["ui_bg_color_1"]

    ui_bg_color_1: str = settings["UI"][skin_type]["ui_bg_color_1"]
    ui_bg_color_2: str = settings["UI"][skin_type]["ui_bg_color_2"]

    ui_font_type: str = settings["UI"]["font_type"]
    ui_font_size: int = settings["UI"]["font_size"]
    ui_font_color_1: str = settings["UI"][skin_type]["ui_font_color_1"]
    ui_font_color_2: str = settings["UI"][skin_type]["ui_font_color_2"]

    ui_btn_bg_color_1: str = settings["UI"][skin_type]["ui_btn_bg_color_1"]
    ui_btn_bg_color_2: str = settings["UI"][skin_type]["ui_btn_bg_color_2"]

    ui_btn_font_color_1: str = settings["UI"][skin_type]["ui_btn_font_color_1"]
    ui_btn_font_color_2: str = settings["UI"][skin_type]["ui_btn_font_color_2"]

    ui_settings = UISettings(
        ui_ttkbootstrap_theme,
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

    return ui_settings
