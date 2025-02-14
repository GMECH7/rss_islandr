import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from general_ui import GeneralUITemplate

from rss_islandr.core.datatypes import UIVariable


class SiteInfoUI(GeneralUITemplate):

    def __init__(
        self,
        ui_inp_vars: dict[str, UIVariable],
        package_dir: Path,
        root: tk.Toplevel,
        canvas_specs: list,
        frame_info: dict[str, list[float]],
    ):
        self.ui_inp_vars = ui_inp_vars

        full_filepath = package_dir / "data/dropdown_lists.json"
        with open(full_filepath, "r", encoding="utf-8") as file_inp:
            self.data = json.load(file_inp)

        self.root = root
        self.frame_info = frame_info
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.canvas_title = canvas_specs[2]
        self.dropdown_list_width = 30
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
        self.activity_var = tk.StringVar()
        self.activity_options = self.data["activity_or_industry"]

        self.land_use_var = tk.StringVar()
        self.land_use_options = self.data["land_uses"]

        self.val_dropdown_dict = {
            "drop_1_00": [
                "inputs_frame",
                1,
                self.activity_var,
                self.activity_options,
                "Select Activity/Industry:",
                "dummy",
            ],
            "drop_1_01": [
                "inputs_frame",
                2,
                self.land_use_var,
                self.land_use_options,
                "Select Land Use:",
                "dummy",
            ],
        }

        self.ui_inputs_merged.update(self.val_dropdown_dict)

        return None

    def _inputs_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "inputs_frame"
        frame_title = "main program"
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

        return None

    def ui(self):
        canvas = tk.Canvas(
            self.root,
            height=self.canvas_height,
            width=self.canvas_width,
            bg=self.background_color,
        )
        canvas.pack()
        self._inputs_frame()
