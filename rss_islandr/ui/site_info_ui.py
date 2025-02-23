import json

import ttkbootstrap as tb
from general_ui import GeneralUITemplate

from rss_islandr.core.config_parser import DROPDOWN_LISTS_JSON_DIR
from rss_islandr.core.datatypes import FramePlacing, UICalcVariable, UIInpVariable, UISettings


class SiteInfoUI(GeneralUITemplate):
    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        parent_frame: tb.Frame,
        frame_geometry_dict: dict[str, FramePlacing],
    ):
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.parent_frame = parent_frame

        with open(DROPDOWN_LISTS_JSON_DIR, "r", encoding="utf-8") as file_inp:
            self.data = json.load(file_inp)

        self.frame_geometry_dict = frame_geometry_dict

        super().__init__(ui_settings, ui_inp_vars, self.frame_geometry_dict)
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()

    def __ui_inputs_entries(self) -> None:
        """
        Definition of inputs. Used in __init__.
        """
        self.site_name = tb.StringVar()
        ui_var_site_name = UIInpVariable(
            frame_tag="site_info_frame",
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
        self.activity_var = tb.StringVar()
        self.activity_options = self.data["activity_or_industry"]

        self.land_use_var = tb.StringVar()
        self.land_use_options = self.data["land_uses"]

        ui_var_activity = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.activity_var,
            rel_pos=1,
            text_val="Select Activity/Industry",
            text_descr=None,
            drop_options=self.activity_options,
            excel_cell="C4",
        )

        ui_var_land_use = UIInpVariable(
            frame_tag="site_info_frame",
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

    def site_info_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "site_info_frame"
        frame_title = "Site inputs"
        frame = self.gt_new_frame(self.parent_frame, frame_tag, frame_title)

        for key in self.ui_inp_vars:
            if self.ui_inp_vars[key].frame_tag == frame_tag and "val" in key:
                self.gt_entry_widget(frame, key)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "drop" in key:
                self.gt_combobox_widget(frame, key)
            else:
                pass

        return None

    def ui(self):
        """ """
        self.site_info_frame()
