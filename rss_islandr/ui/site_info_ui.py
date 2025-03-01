import json
import locale

import ttkbootstrap as tb
from general_btns_ui import GeneralBtnsUI
from general_ui import GeneralUITemplate

from rss_islandr.core.config_parser import DROPDOWN_LISTS_JSON_DIR
from rss_islandr.core.datatypes import FramePlacing, UICalcVariable, UIInpVariable, UISettings

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # or 'C.UTF-8', 'en_GB.UTF-8', etc.


class SiteInfoUI(GeneralUITemplate):
    def __init__(
        self,
        parent_navbar_frame: tb.Frame,
        parent_frame: tb.Frame,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        frame_geometry_dict: dict[str, FramePlacing],
        widgets_reconfigured,
    ):
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.gnrl_btns_ui = GeneralBtnsUI(ui_settings, ui_inp_vars, ui_calc_vars, widgets_reconfigured)

        with open(DROPDOWN_LISTS_JSON_DIR, "r", encoding="utf-8") as file_inp:
            self.data = json.load(file_inp)

        self.frame_geometry_dict = frame_geometry_dict

        super().__init__(ui_settings, ui_inp_vars, self.frame_geometry_dict, widgets_reconfigured=widgets_reconfigured)
        self.__ui_inputs_dates()
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()

    def __ui_inputs_dates(self):
        """
        Definition of date widget inputs.
        """
        self.date_assessed = tb.StringVar()
        date_var = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.date_assessed,
            rel_pos=1,
            text_val="Assessment date",
            text_descr=None,
            excel_cell="E3",
        )
        self.ui_inp_vars.update({"date_0_00": date_var})

    def __ui_inputs_entries(self) -> None:
        """
        Definition of entry widget inputs.
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
        Definition of dropdown widget inputs.
        """
        self.activity_var = tb.StringVar()
        self.activity_options = self.data["activity_or_industry"]

        self.land_use_var = tb.StringVar()
        self.land_use_options = self.data["land_uses"]

        self.soil_type_var = tb.StringVar()
        self.soil_type_options = self.data["soil_type"]

        ui_var_activity = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.activity_var,
            rel_pos=2,
            text_val="Select Activity/Industry",
            text_descr=None,
            drop_options=self.activity_options,
            excel_cell="C4",
        )

        ui_var_land_use = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.land_use_var,
            rel_pos=3,
            text_val="Select Land Use",
            text_descr=None,
            drop_options=self.land_use_options,
            excel_cell="J2",
        )

        ui_var_soil_type = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.soil_type_var,
            rel_pos=4,
            text_val="Select Soil type",
            text_descr=None,
            drop_options=self.soil_type_options,
            excel_cell="J3",
        )

        self.ui_inp_vars.update({"drop_0_00": ui_var_activity})
        self.ui_inp_vars.update({"drop_0_01": ui_var_land_use})
        self.ui_inp_vars.update({"drop_0_02": ui_var_soil_type})

        return None

    def site_info_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        frame_tag = "site_info_frame"
        frame_title = "Site inputs"
        frame = self.gt_new_frame(self.__parent_frame, frame_tag, frame_title)

        for key in self.ui_inp_vars:
            if self.ui_inp_vars[key].frame_tag == frame_tag and "val" in key:
                self.gt_entry_widget(frame, key, 2)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "drop" in key:
                self.gt_combobox_widget(frame, key, 2)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "date" in key:
                self.gt_date_entry_widget(frame, key, 2)
            else:
                pass

        label = tb.Label(frame, text="Longtitude (Updated automatically)")
        label.grid(column=0, row=5, sticky="we")

        lat_entry = tb.Entry(frame, textvariable=self.ui_inp_vars["map_0_00"].tk_var)
        lat_entry.grid(column=1, row=5, sticky="we")

        lng_entry = tb.Entry(frame, textvariable=self.ui_inp_vars["map_0_01"].tk_var)
        lng_entry.grid(column=2, row=5, sticky="we")

    def ui(self):
        """ """
        self.gnrl_btns_ui.file_menu_btn(self.__parent_navbar_frame)
        self.site_info_frame()
