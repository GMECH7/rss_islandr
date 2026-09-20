from dataclasses import dataclass, field
from typing import TypedDict, Union

import ttkbootstrap as tb

TkValues = tb.StringVar

TkWidgets = Union[tb.Button, tb.Entry]


class SeverityDict(TypedDict):
    alias: str
    weight: float


class ControlsDict(TypedDict):
    alias: str
    descr: str
    severity: dict[str, SeverityDict]


class ParametersDict(TypedDict):
    alias: str
    weight: float


class ReceptorParametersDict(TypedDict):
    available_pathways: list[str]
    parameter: dict[str, ParametersDict]


class PolygonDataDict(TypedDict):
    """Data structure to hold polygon information coming from JavaScript"""

    unique_id: str
    type: str
    name: str
    coordinates: list[list[float]]
    area_km2: float
    node_count: int


@dataclass
class UIInpVariable:
    frame_tag: str
    tk_var: TkValues
    rel_pos: int
    text_val: str
    val_default: str | None = ""
    text_descr: str | None = None
    drop_options: list[str] | None = None
    excel_cell: str | None = None
    pdf_table_name: str | None = ""
    state: str = field(default="enabled")


@dataclass
class UICalcVariable:
    tk_var: tb.StringVar
    excel_cell: str | None = None


@dataclass
class FramePlacing:
    x_l: float
    x_r: float
    y_u: float
    y_d: float
    n_row: int | None = None
    n_col: int | None = None


@dataclass
class UISettings:
    ui_ttkbootstrap_theme: str
    ui_title_font_type: str
    ui_title_font_size: int
    ui_title_font_color: str
    ui_title_offset: float
    ui_title_offset: float
    ui_bg_color_1: str
    ui_bg_color_2: str
    ui_font_type: str
    ui_font_size: int
    ui_font_color_1: str
    ui_font_color_2: str
    ui_btn_bg_color_1: str
    ui_btn_bg_color_2: str
    ui_btn_font_color_1: str
    ui_btn_font_color_2: str
