from typing import TypedDict


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
