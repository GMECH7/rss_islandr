import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Optional, TypedDict, Union

TkValues = Union[tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar]


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
class UIVariable:
    frame_tag: str
    tk_var: TkValues
    rel_pos: int
    text_val: str
    text_descr: Optional[str] = None
    drop_options: Optional[List[str]] = None
    excel_cell: Optional[str] = None
    state: str = field(default="enabled")
