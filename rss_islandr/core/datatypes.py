from dataclasses import dataclass, field
from typing import List, Optional, TypedDict, Union

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


@dataclass
class UIInpVariable:
    frame_tag: str
    tk_var: TkValues
    rel_pos: int
    text_val: str
    val_default: Optional[str] = ""
    text_descr: Optional[str] = None
    drop_options: Optional[List[str]] = None
    excel_cell: Optional[str] = None
    state: str = field(default="enabled")


@dataclass
class UICalcVariable:
    tk_var: tb.StringVar
    excel_cell: Optional[str] = None


@dataclass
class FramePlacing:
    x_l: float
    x_r: float
    y_u: float
    y_d: float
    n_row: Optional[int] = None
    n_col: Optional[int] = None


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
