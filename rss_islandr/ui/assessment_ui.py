import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import TypedDict

from general_ui import GeneralUITemplate

from rss_islandr.assessment import risk_calc, risk_color_assignment
from rss_islandr.data_readers import ReceptorAliases, ReceptorFactorsFetcher, RisksDataFetcher


class RiskSelectionDict(TypedDict):
    var: tk.StringVar
    weights: dict[str, float]


class AssessmentUI(GeneralUITemplate):

    def __init__(
        self,
        package_dir: Path,
        root: tk.Toplevel,
        canvas_specs: list,
        frame_info: dict[str, list[float]],
    ):
        filepath_risk_factors = package_dir / "data/risk_factors.json"
        filepath_receptor_factors = package_dir / "data/receptor_factors.json"
        self.hazard_fetcher = RisksDataFetcher(filepath_risk_factors)
        self.receptor_fetcher = ReceptorFactorsFetcher(filepath_receptor_factors)
        self.receptor_aliases = ReceptorAliases(filepath_receptor_factors)

        self.root = root
        self.frame_info = frame_info
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.canvas_title = canvas_specs[2]
        self.dropdown_list_width = 30

        self.val_dropdown_dict = {}
        self.__receptor_alias_to_key_dict = {
            k: v for (v, k) in self.receptor_aliases.getter().items()
        }
        self.__receptor_key_to_alias = self.receptor_aliases.getter()

        self.__source_keys = ["IN"]
        self.__pathway_keys = ["SL", "GW", "SW", "AR", "SD"]
        self.__receptor_keys = [f"{pathway}_receptor" for pathway in self.__pathway_keys]
        self.__source_pathway_keys = self.__source_keys + self.__pathway_keys
        self.__source_pathway_receptor_keys = self.__source_pathway_keys + self.__receptor_keys

        self.__init__risk_selection_dict()
        self.__init__receptor_risk_selection_dict()

        super().__init__(self.root, self.frame_info, self.canvas_height, self.canvas_width)

        self.__init__source_pathway_dropdown()
        self.__init__receptor_dropdown()
        self.__init__calculated_risks_dict()

    def __init__risk_selection_dict(self):
        """
        This is a method used in the __init__.

        It initializes the risk_selection_dict with the following format:
        key: f'{<source or pathway_key>}'
        Value: empty dictionary which when populated is of type {<mechanism_alias>:RiskSelectionDict}.

        This dictionary is used to map severity aliases used in the dropdown lists to their weight value.
        """
        self.__risk_selection = {}
        for key in self.__source_pathway_keys:
            self.__risk_selection.update({f"{key}_frame": {}})

    def __init__receptor_risk_selection_dict(self):
        """
        This is a method used in the __init__.
        """
        self.__receptor_risk_selection = {}
        for key in self.__receptor_keys:
            self.__receptor_risk_selection.update({f"{key}_frame": {}})

    def __init__calculated_risks_dict(self):
        """ """
        self.__calculated_risks = {}
        for key in self.__source_pathway_receptor_keys:
            self.__calculated_risks.update({f"{key}_frame": tk.StringVar(value="0.0")})

    def __init__source_pathway_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used in source and pathway calculations dropdown lists.
        """
        for key in self.__source_pathway_keys:
            mechanisms_dict = self.hazard_fetcher.getter(key)["mechanism"]
            for i, mechanism_key in enumerate(mechanisms_dict):
                mechanism_alias = self.hazard_fetcher.getter(key, mechanism_key)["alias"]
                severity_dict = self.hazard_fetcher.getter(key, mechanism_key)["severity"]

                dropdown_severity = []
                alias_to_weight = {}

                for severity_key in severity_dict:
                    severity_alias = severity_dict[severity_key]["alias"]
                    severity_weight = severity_dict[severity_key]["weight"]
                    dropdown_severity.append(severity_alias)
                    alias_to_weight[severity_alias] = severity_weight

                var = tk.StringVar()
                var.set(dropdown_severity[0])

                # Store weight mapping for later use
                self.__risk_selection[f"{key}_frame"].update(
                    {mechanism_alias: {"var": var, "weights": alias_to_weight}}
                )

                self.val_dropdown_dict[f"drop_{key}_1_0{i}"] = [
                    f"{key}_frame",
                    i + 1,
                    var,
                    dropdown_severity,
                    mechanism_alias,
                    "dummy",
                ]

            self.ui_inputs_merged.update(self.val_dropdown_dict)

        return None

    def __init__receptor_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used receptor calculations dropdown lists.
        """

        for key in self.__receptor_keys:

            dropdown_available_pathways = list(self.receptor_aliases.getter().values())
            dropdown_receptor_param = []
            param_alias_to_weight = {}

            parameters_dict = self.receptor_fetcher.getter(key)["parameter"]
            for parameter_key in parameters_dict:
                parameter_alias = self.receptor_fetcher.getter(key, parameter_key)["alias"]
                parameter_weight = self.receptor_fetcher.getter(key, parameter_key)["weight"]
                param_alias_to_weight[parameter_alias] = parameter_weight
                dropdown_receptor_param.append(parameter_alias)

            pathway_var = tk.StringVar()
            pathway_var.set(dropdown_available_pathways[0])

            receptor_param = tk.StringVar()
            receptor_param.set(dropdown_receptor_param[0])

            # Store weight mapping for later use
            self.__receptor_risk_selection[f"{key}_frame"].update(
                {
                    f"{key}_frame": {
                        "pathway": pathway_var,
                        "var": receptor_param,
                        "weights": param_alias_to_weight,
                    }
                }
            )
            self.val_dropdown_dict[f"drop_{key}_1_0"] = [
                f"{key}_frame",
                0,
                pathway_var,
                dropdown_available_pathways,
                f"{key}_receptor",
                "dummy",
            ]

            self.val_dropdown_dict[f"drop_{key}_1_1"] = [
                f"{key}_frame",
                1,
                receptor_param,
                dropdown_receptor_param,
                f"{key}_receptor",
                "dummy",
            ]

            self.ui_inputs_merged.update(self.val_dropdown_dict)

    def _light_bulb(self, frame, color: str) -> None:
        """ """
        light = tk.Label(frame, text=" ", bg=color, width=4, height=2)
        light.grid(row=len(self.val_dropdown_dict) + 1, column=1, pady=10)

    def __source_pathway_frame_creator(self, frame_tag: str, frame_title: str) -> tk.Frame:
        """ """
        frame = self.general_template_frames(frame_tag, frame_title)
        new_col_criterion = self.frame_info[frame_tag][-1]
        for param_dropdown in list(self.val_dropdown_dict.keys()):
            if self.val_dropdown_dict[param_dropdown][0] == frame_tag:
                self.general_template_dropdown(
                    frame,
                    param_dropdown,
                    new_col_criterion,
                )

        # Add the "Print Weights" button
        print_button = ttk.Button(
            frame,
            text="Print Weights",
            command=lambda: self.__calculate_source_pathway_risk(frame, frame_tag),
        )
        print_button.grid(row=len(self.val_dropdown_dict) + 1, column=0, pady=10)
        self._light_bulb(frame, "white")

        return frame

    def __receptor_frame_creator(self, frame_tag: str, frame_title: str) -> tk.Frame:
        """ """
        frame = self.general_template_frames(frame_tag, frame_title)
        new_col_criterion = self.frame_info[frame_tag][-1]

        for param_dropdown in list(self.val_dropdown_dict.keys()):
            if self.val_dropdown_dict[param_dropdown][0] == frame_tag:
                self.general_template_dropdown(
                    frame,
                    param_dropdown,
                    new_col_criterion,
                )

        # Add the "Print Weights" button
        print_button = ttk.Button(
            frame,
            text="Print Weights",
            command=lambda: self.__calculate_receptor_total_risk(frame, frame_tag),
        )
        print_button.grid(row=len(self.val_dropdown_dict) + 1, column=0, pady=10)
        self._light_bulb(frame, "white")

        return frame

    def source_frame(self) -> None:
        """ """
        frame_tag = "IN_frame"
        frame_title = self.hazard_fetcher.getter("IN")["alias"]
        self.__source_pathway_frame_creator(frame_tag, frame_title)

    def pathway_frames(self) -> None:
        """Method assembling the pathway frames."""

        for risk_key in self.__source_pathway_keys[1:]:
            frame_tag = f"{risk_key}_frame"
            frame_title = f"{self.hazard_fetcher.getter(risk_key)["alias"]} pathway"
            self.__source_pathway_frame_creator(frame_tag, frame_title)

    def receptor_frames(self) -> None:
        """ """
        for risk_receptor_key in self.__receptor_keys:
            frame_tag = f"{risk_receptor_key}_frame"
            frame_title = f"{self.__receptor_key_to_alias[risk_receptor_key[:2]]} Receptor"
            self.__receptor_frame_creator(frame_tag, frame_title)

    def __calculate_source_pathway_risk(self, frame: tk.Frame, frame_tag: str):
        """
        Retrieves selected dropdown values and prints their corresponding weights.
        """
        weights = []
        for data in self.__risk_selection[frame_tag].values():
            selected_alias = data["var"].get()
            selected_weight = data["weights"].get(selected_alias, 0.0)
            weights.append(selected_weight)

        risk = risk_calc(weights)

        color = risk_color_assignment(risk)

        self._light_bulb(frame, color)
        self.__calculated_risks[frame_tag].set(f"{risk}")

        print(f"{selected_alias} -> Weights: {weights} -> risk calc: {risk}")

    def __calculate_receptor_total_risk(self, frame: tk.Frame, frame_tag: str):

        data = self.__receptor_risk_selection[frame_tag][frame_tag]

        pathway_alias = data["pathway"].get()
        pathway_key = self.__receptor_alias_to_key_dict[pathway_alias]

        receptor_alias = data["var"].get()
        receptor_weight = data["weights"].get(receptor_alias, 0.0)

        source_risk = float(self.__calculated_risks["IN_frame"].get())
        pathway_risk = float(self.__calculated_risks[f"{pathway_key}_frame"].get())

        receptor_risk = risk_calc([source_risk, pathway_risk, receptor_weight])

        color = risk_color_assignment(receptor_risk)

        self._light_bulb(frame, color)
        self.__calculated_risks[frame_tag].set(f"{receptor_risk}")

        print(
            f"{receptor_alias} -> Weights: {[source_risk, pathway_risk, receptor_weight]} -> risk calc: {receptor_risk}"
        )

    def ui(self):
        canvas = tk.Canvas(
            self.root,
            height=self.canvas_height,
            width=self.canvas_width,
            bg=self.background_color,
        )
        canvas.pack()
        self.source_frame()
        self.pathway_frames()
        self.receptor_frames()
