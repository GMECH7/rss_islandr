import tkinter as tk
from pathlib import Path
from tkinter import ttk

from general_ui import GeneralUITemplate

from rss_islandr.assessment import risk_calc
from rss_islandr.data_readers import RisksDataFetcher, ReceptorFactorsFetcher


class AssessmentUI(GeneralUITemplate):

    def __init__(
        self,
        package_dir: Path,
        root: tk.Toplevel,
        canvas_specs: list,
        frame_info: dict[str, list[float]],
    ):
        full_filepath = package_dir / "data/risk_factors.json"
        full_filepath_2 = package_dir / "data/receptor_factors.json"
        self.hazard_fetcher = RisksDataFetcher(full_filepath)
        self.receptor_fetcher = ReceptorFactorsFetcher(full_filepath_2)

        self.root = root
        self.frame_info = frame_info
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.canvas_title = canvas_specs[2]
        self.dropdown_list_width = 30

        self.val_dropdown_dict = {}
        self.risk_keys = ["IN", "SL", "GW", "SW", "AR", "SD"]
        self.selected_weights = {
            "IN_frame": {},
            "SL_frame": {},
            "GW_frame": {},
            "SW_frame": {},
            "AR_frame": {},
            "SD_frame": {},
            "SL_receptor_frame": {},
        }

        self.calculated_risks = {
            "IN_frame": tk.StringVar(value="0.0"),
            "SL_frame": tk.StringVar(value="0.0"),
            "GW_frame": tk.StringVar(value="0.0"),
            "SW_frame": tk.StringVar(value="0.0"),
            "AR_frame": tk.StringVar(value="0.0"),
            "SD_frame": tk.StringVar(value="0.0"),
            "SL_receptor_frame": tk.StringVar(value="0.0"),
        }

        super().__init__(self.root, self.frame_info, self.canvas_height, self.canvas_width)
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()
        self.__ui_inputs_dropdown_2()

    def __ui_inputs_entries(self) -> None:
        """
        Definition of inputs. Used in __init__.
        """
        self.site_name = tk.StringVar()

        self.val_entries_dict = {
            "val_1_00": [
                "inputs_frame",
                0,
                self.site_name,
                "dummy",
                "Site name",
                "dummy",
            ],
        }

        self.ui_inputs_merged.update(self.val_entries_dict)

    def __ui_inputs_dropdown(self) -> None:
        """
        Method used in __init__.
        """
        for key in self.risk_keys:
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
                self.selected_weights[f"{key}_frame"].update(
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

    def __ui_inputs_dropdown_2(self) -> None:

        for key in ["SL"]:

            dropdown_available_pathways = self.receptor_fetcher.getter(key)["available_pathways"]
            dropdown_parameters = []
            param_alias_to_weight = {}
            parameters_dict = self.receptor_fetcher.getter(key)["parameter"]
            for parameter_key in parameters_dict:
                parameter_alias = self.receptor_fetcher.getter(key, parameter_key)["alias"]
                parameter_weight = self.receptor_fetcher.getter(key, parameter_key)["weight"]
                param_alias_to_weight[parameter_alias] = parameter_weight
                dropdown_parameters.append(parameter_alias)

            pathway_var = tk.StringVar()
            pathway_var.set(dropdown_available_pathways)

            var = tk.StringVar()
            var.set(dropdown_parameters[0])

            # Store weight mapping for later use
            self.selected_weights[f"{key}_receptor_frame"].update(
                {
                    f"{key}_receptor_frame": {
                        "var": var,
                        "pathway": pathway_var,
                        "weights": param_alias_to_weight,
                    }
                }
            )
            self.val_dropdown_dict[f"drop_receptor_{key}_1_0"] = [
                f"{key}_receptor_frame",
                0,
                pathway_var,
                dropdown_available_pathways,
                f"{key}_receptor",
                "dummy",
            ]

            self.val_dropdown_dict[f"drop_receptor_{key}_1_1"] = [
                f"{key}_receptor_frame",
                1,
                var,
                dropdown_parameters,
                f"{key}_receptor",
                "dummy",
            ]

            self.ui_inputs_merged.update(self.val_dropdown_dict)

    def _light_bulb(self, frame, color: str) -> None:
        """ """
        light = tk.Label(frame, text=" ", bg=color, width=4, height=2)
        light.grid(row=len(self.val_dropdown_dict) + 1, column=1, pady=10)

    def __frame_creator(self, frame_tag: str, frame_title: str) -> tk.Frame:
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
            command=lambda: self.print_selected_weights(frame, frame_tag),
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

    def industry_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "IN_frame"
        frame_title = "main program"
        self.__frame_creator(frame_tag, frame_title)

    def pathway_frames(self) -> None:
        """Method assembling the pathway frames."""

        for risk_key in self.risk_keys[1:]:
            frame_tag = f"{risk_key}_frame"
            frame_title = risk_key
            self.__frame_creator(frame_tag, frame_title)

    def receptor_frames(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "SL_receptor_frame"
        frame_title = "main program"
        self.__receptor_frame_creator(frame_tag, frame_title)

    def __calculate_receptor_total_risk(self, frame, frame_tag):

        pathway_used = self.selected_weights[frame_tag][frame_tag]["pathway"].get()
        data = self.selected_weights[frame_tag][frame_tag]
        receptor_alias = data["var"].get()
        receptor_weight = data["weights"].get(receptor_alias, 0.0)
        source_risk = float(self.calculated_risks["IN_frame"].get())
        pathway_risk = float(self.calculated_risks[f"{pathway_used}_frame"].get())

        receptor_risk = risk_calc([source_risk, pathway_risk, receptor_weight])

        if receptor_risk <= 0.1:
            color = "green"
        elif 0.1 < receptor_risk <= 0.3:
            color = "yellow"
        else:
            color = "red"

        self._light_bulb(frame, color)
        self.calculated_risks[frame_tag].set(f"{receptor_risk}")

        print(
            f"{receptor_alias} -> Weights: {[source_risk, pathway_risk, receptor_weight]} -> risk calc: {receptor_risk}"
        )

    def print_selected_weights(self, frame, frame_tag):
        """
        Retrieves selected dropdown values and prints their corresponding weights.
        """
        weights = []
        for data in self.selected_weights[frame_tag].values():
            selected_alias = data["var"].get()
            selected_weight = data["weights"].get(selected_alias, 0.0)
            weights.append(selected_weight)

        risk = risk_calc(weights)

        if risk <= 0.1:
            color = "green"
        elif 0.1 < risk <= 0.3:
            color = "yellow"
        else:
            color = "red"

        self._light_bulb(frame, color)
        self.calculated_risks[frame_tag].set(f"{risk}")

        print(f"{selected_alias} -> Weights: {weights} -> risk calc: {risk}")

    def ui(self):
        canvas = tk.Canvas(
            self.root,
            height=self.canvas_height,
            width=self.canvas_width,
            bg=self.background_color,
        )
        canvas.pack()
        self.industry_frame()
        self.pathway_frames()
        self.receptor_frames()
