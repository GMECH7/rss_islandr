import tkinter as tk
from pathlib import Path
from tkinter import ttk

from general_ui import GeneralUITemplate

from rss_islandr.assessment import risk_calc
from rss_islandr.data_readers import RisksDataFetcher


class AssessmentUI(GeneralUITemplate):

    def __init__(
        self,
        package_dir: Path,
        root: tk.Toplevel,
        canvas_specs: list,
        frame_info: dict[str, list[float]],
    ):
        full_filepath = package_dir / "data/risk_factors.json"
        self.hazard_fetcher = RisksDataFetcher(full_filepath)

        self.root = root
        self.frame_info = frame_info
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.canvas_title = canvas_specs[2]
        self.dropdown_list_width = 30

        self.val_dropdown_dict = {}
        self.selected_weights = {"IN_frame": {}, "SL_frame": {}}

        super().__init__(self.root, self.frame_info, self.canvas_height, self.canvas_width)
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()

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
        for key in ["IN", "SL"]:
            mechanisms_dict = self.hazard_fetcher.getter(key)["mechanism"]
            for i, mechanism_key in enumerate(mechanisms_dict):
                mechanism_alias = self.hazard_fetcher.getter(key, mechanism_key)["alias"]
                severity_dict = self.hazard_fetcher.getter(key, mechanism_key)["severity"]

                dropdown_severity = []
                alias_to_weight = {}

                for severity_key in severity_dict:
                    severity_alias = severity_dict[severity_key]["alias"]
                    severity_weight = severity_dict[severity_key]["weight"]
                    dropdown_severity.append(severity_dict[severity_key]["alias"])
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
        # print(self.ui_inputs_merged)
        return None

    def _light_bulb(self, frame, color: str) -> None:
        """ """
        light = tk.Label(frame, text=" ", bg=color, width=4, height=2)
        light.grid(row=len(self.val_dropdown_dict) + 1, column=1, pady=10)

    def _inputs_frame(self, frame_tag, frame_title) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame = self.general_template_frames(frame_tag, frame_title)
        new_col_criterion = self.frame_info[frame_tag][-1]

        for param_entry in list(self.val_entries_dict.keys()):
            if self.val_entries_dict[param_entry][0] == frame_tag:
                self.general_template_entries(
                    frame,
                    param_entry,
                    new_col_criterion,
                )

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

    def _industry_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "IN_frame"
        frame_title = "main program"
        self._inputs_frame(frame_tag, frame_title)

    def _soil_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "SL_frame"
        frame_title = "Soil Risk"
        self._inputs_frame(frame_tag, frame_title)

    def print_selected_weights(self, frame, frame_tag):
        """
        Retrieves selected dropdown values and prints their corresponding weights.
        """
        weights = []
        for data in self.selected_weights[frame_tag].values():
            print(111111111111111, data)
            selected_alias = data["var"].get()
            selected_weight = data["weights"].get(selected_alias, 0.0)
            weights.append(selected_weight)

        risk = risk_calc(weights)
        print(f"{selected_alias} -> Weights: {weights} -> risk calc: {risk}")

        if risk <= 0.1:
            color = "green"
        elif 0.1 < risk <= 0.3:
            color = "yellow"
        else:
            color = "red"

        self._light_bulb(frame, color)

    def ui(self):
        canvas = tk.Canvas(
            self.root,
            height=self.canvas_height,
            width=self.canvas_width,
            bg=self.background_color,
        )
        canvas.pack()
        self._industry_frame()
        self._soil_frame()
