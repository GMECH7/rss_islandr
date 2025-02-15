import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from general_ui import GeneralUITemplate

from rss_islandr.core.datatypes import UISettings, UIVariable


class AnotherException(Exception):
    pass


class SiteInfoUI(GeneralUITemplate):

    def __init__(
        self,
        ui_inp_vars: dict[str, UIVariable],
        ui_settings: UISettings,
        package_dir: Path,
        root: tk.Toplevel,
        canvas_specs: list,
        frame_infos_dict,
    ):
        self.ui_inp_vars = ui_inp_vars
        self.ui_settings = ui_settings

        full_filepath = package_dir / "data/dropdown_lists.json"
        with open(full_filepath, "r", encoding="utf-8") as file_inp:
            self.data = json.load(file_inp)

        self.root = root
        self.frame_infos_dict = frame_infos_dict
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.canvas_title = canvas_specs[2]

        super().__init__(
            ui_inp_vars,
            ui_settings,
            self.root,
            self.frame_infos_dict["0"],
            self.canvas_height,
            self.canvas_width,
        )
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()

    def __ui_inputs_entries(self) -> None:
        """
        Definition of inputs. Used in __init__.
        """
        self.site_name = tk.StringVar()
        ui_var_site_name = UIVariable(
            frame_tag="inputs_frame",
            tk_var=self.site_name,
            rel_pos=0,
            text_val="Site name",
            text_descr=None,
            excel_cell="C2",
        )

        self.ui_inp_vars.update({"val_0_00": ui_var_site_name})

    def __ui_inputs_dropdown(self) -> None:
        """
        Method used in __init__.
        """
        self.activity_var = tk.StringVar()
        self.activity_options = self.data["activity_or_industry"]

        self.land_use_var = tk.StringVar()
        self.land_use_options = self.data["land_uses"]

        ui_var_activity = UIVariable(
            frame_tag="inputs_frame",
            tk_var=self.activity_var,
            rel_pos=1,
            text_val="Select Activity/Industry",
            text_descr=None,
            drop_options=self.activity_options,
            excel_cell="C4",
        )

        ui_var_land_use = UIVariable(
            frame_tag="inputs_frame",
            tk_var=self.land_use_var,
            rel_pos=2,
            text_val="Select Land Use",
            text_descr=None,
            drop_options=self.land_use_options,
            excel_cell="J2",
        )

        self.ui_inp_vars.update({"drop_0_00": ui_var_activity})
        self.ui_inp_vars.update({"drop_0_01": ui_var_land_use})

        return None

    def inputs_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "inputs_frame"
        frame_title = "main program"
        frame = self.general_template_frames(frame_tag, frame_title)

        for key in self.ui_inp_vars:
            if self.ui_inp_vars[key].frame_tag == frame_tag and "val" in key:
                self.general_template_entries(frame, key)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "drop" in key:
                self.general_template_dropdown(frame, key)
            else:
                pass

        return None

    def ui(self):
        canvas = tk.Canvas(
            self.root,
            height=self.canvas_height,
            width=self.canvas_width,
            bg=self.ui_settings.ui_bg_color_1,
        )
        canvas.pack()
        self.inputs_frame()
