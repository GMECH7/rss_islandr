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
        self.__widgets_reconfigured = widgets_reconfigured
        self.gnrl_btns_ui = GeneralBtnsUI(ui_settings, ui_inp_vars, ui_calc_vars, widgets_reconfigured)

        with open(DROPDOWN_LISTS_JSON_DIR, "r", encoding="utf-8") as file_inp:
            self.data = json.load(file_inp)

        self.frame_geometry_dict = frame_geometry_dict

        super().__init__(ui_settings, ui_inp_vars, self.frame_geometry_dict, widgets_reconfigured=widgets_reconfigured)
        self.__ui_inputs_dates()
        self.__ui_inputs_entries()
        self.__ui_inputs_dropdown()

    # self.__ui_inputs_nested_dropdown()

    def __ui_inputs_dates(self):
        """
        Definition of date widget inputs.
        """
        self.date_assessed = tb.StringVar()
        date_var = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.date_assessed,
            rel_pos=2,
            text_val="Assessment date",
            text_descr=None,
            excel_cell="C3",
        )

        self.date_oper_start = tb.StringVar()
        date_oper_start_var = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.date_oper_start,
            rel_pos=7,
            text_val="Operation start & end dates",
            text_descr=None,
            excel_cell="M3",
        )
        self.date_oper_end = tb.StringVar()
        date_oper_end_var = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.date_oper_end,
            rel_pos=7,
            text_val="Operation start & end dates",
            text_descr=None,
            excel_cell="M4",
        )
        self.ui_inp_vars.update({"date_0_00": date_var})
        self.ui_inp_vars.update({"datte_0_01": date_oper_start_var})
        self.ui_inp_vars.update({"datte_0_02": date_oper_end_var})

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

        self.site_status_var = tb.StringVar()
        self.site_status_var.set("")
        self.site_status_options = self.data["site_status"]

        self.soil_type_var = tb.StringVar()
        self.soil_type_options = self.data["soil_type"]

        ui_var_activity = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.activity_var,
            rel_pos=3,
            text_val="Select activity/industry",
            text_descr=None,
            drop_options=self.activity_options,
            excel_cell="H2",
        )

        ui_var_land_use = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.land_use_var,
            rel_pos=4,
            text_val="Select land Use",
            text_descr=None,
            drop_options=self.land_use_options,
            excel_cell="H3",
        )

        ui_var_soil_type = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.soil_type_var,
            rel_pos=5,
            text_val="Select soil type",
            text_descr=None,
            drop_options=self.soil_type_options,
            excel_cell="H4",
        )

        ui_var_site_status = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.site_status_var,
            rel_pos=6,
            text_val="Select site status",
            text_descr=None,
            drop_options=self.site_status_options,
            excel_cell="M2",
        )

        self.site_status_var.trace_add("write", self.update_date_widgets)
        self.ui_inp_vars.update({"drop_0_00": ui_var_activity})
        self.ui_inp_vars.update({"drop_0_01": ui_var_land_use})
        self.ui_inp_vars.update({"drop_0_02": ui_var_site_status})
        self.ui_inp_vars.update({"drop_0_03": ui_var_soil_type})

        return None

    def __ui_inputs_nested_dropdown(self):
        """Initialize the nested dropdown for soil types."""
        # Dictionary of soil types
        self.soil_types_dict = self.data["soil_types"]

        # First dropdown: Select soil category
        self.soil_type_1_var = tb.StringVar()
        self.soil_type_1_options = list(self.soil_types_dict.keys())
        self.soil_type_1_var.set(self.soil_type_1_options[0])  # Set default value

        # Create the first dropdown UI element
        ui_var_soil_type_1 = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.soil_type_1_var,
            rel_pos=4,
            text_val="Select soil type",
            val_default=self.soil_type_1_options[0],
            text_descr=None,
            drop_options=self.soil_type_1_options,
            excel_cell="J3",
        )

        # Second dropdown: Select soil type (dependent on the first dropdown)
        self.soil_type_2_var = tb.StringVar()

        # Bind the update function to the first dropdown
        self.soil_type_1_var.trace_add("write", self.update_soil_options)

        # Initialize the second dropdown options based on the first dropdown's default value
        self.soil_type_2_options = self.soil_types_dict[self.soil_type_1_var.get()]
        self.soil_type_2_var.set(self.soil_type_2_options[0])  # Set default value

        # Create the second dropdown UI element
        self.ui_var_soil_type_2 = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=self.soil_type_2_var,
            rel_pos=4,
            text_val="Select soil type",
            val_default=self.soil_type_2_options[0],
            text_descr=None,
            drop_options=self.soil_type_2_options,
            excel_cell="J3",
        )
        print(self.ui_var_soil_type_2.drop_options)

        # Add the dropdowns to the UI variables dictionary
        self.ui_inp_vars.update({"ndro_0_00": ui_var_soil_type_1})
        self.ui_inp_vars.update({"ndro_0_01": self.ui_var_soil_type_2})

    def update_soil_options(self, *args):
        """Update the options in the second dropdown based on the first dropdown's selection."""
        selected_category = self.soil_type_1_var.get()

        # Update the options for the second dropdown
        self.soil_type_2_options = self.soil_types_dict[selected_category]
        self.soil_type_2_var.set(self.soil_type_2_options[0])  # Set default value

        # Update the dropdown options in the UI
        self.ui_var_soil_type_2.drop_options = self.soil_type_2_options

        # Update the Combobox widget's values
        if hasattr(self.ui_var_soil_type_2, "combobox"):  # Ensure the Combobox widget exists
            self.ui_var_soil_type_2.combobox["values"] = self.soil_type_2_options

    def update_date_widgets(self, *args):
        selected_option = self.site_status_var.get()

        if selected_option == "Active" or selected_option == "Proposed":
            # Show only the start date widget
            self.start_end_oper_label.config(text="Operation start date")
            self.start_end_oper_label.grid(row=7, column=0, sticky="ew")
            self.start_date_entry.grid(row=7, column=1, sticky="ew")
            self.end_date_entry.grid_remove()
        elif selected_option == "Legacy":
            self.start_end_oper_label.config(text="Operation start & end dates")
            self.start_end_oper_label.grid(row=7, column=0, sticky="ew")
            self.start_date_entry.grid(row=7, column=1, sticky="ew")
            self.end_date_entry.grid(row=7, column=2, sticky="ew")
        else:
            self.start_end_oper_label.grid_remove()
            self.start_date_entry.grid_remove()
            self.end_date_entry.grid_remove()

    def site_info_frame(self) -> None:
        """
        Inputs frame for main-specific inputs.
        """
        # TODO I will have to make dynamic the DateEntries
        # TODO I have to check the nested comboboxes
        frame_tag = "site_info_frame"
        frame_title = "Site inputs"
        frame = self.gt_new_frame(self.__parent_frame, frame_tag, frame_title)
        self.frame = frame
        for key in self.ui_inp_vars:
            if self.ui_inp_vars[key].frame_tag == frame_tag and "val" in key:
                self.gt_entry_widget(frame, key, 2)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "drop" in key:
                self.gt_combobox_widget(frame, key, 2)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "date" in key:
                self.gt_date_entry_widget(frame, key, 2)
            elif self.ui_inp_vars[key].frame_tag == frame_tag and "ndro" in key and float(key[-2:]) % 2 == 0:
                print(float(key[-2:]) % 2)
                self.gt_nested_combobox_widget(frame, key, 1)
            else:
                pass

        label = tb.Label(frame, text="Latitude & Longitude)")
        label.grid(column=0, row=1, sticky="we")

        lat_entry = tb.Entry(frame, textvariable=self.ui_inp_vars["map_0_00"].tk_var)
        lat_entry.grid(column=1, row=1, sticky="we")

        lng_entry = tb.Entry(frame, textvariable=self.ui_inp_vars["map_0_01"].tk_var)
        lng_entry.grid(column=2, row=1, sticky="we")
        # TODO This must become dynamic and the entry widget should be used
        self.start_end_oper_label = tb.Label(self.frame, text="")
        self.start_date_entry = tb.DateEntry(
            self.frame, bootstyle=self.ui_settings.ui_bg_color_1, dateformat="%Y-%m-%d"
        )
        self.start_date_entry.bind(
            "<FocusOut>", lambda event: self.__update_date_var(event, self.start_date_entry, "datte_0_01")
        )
        self.__widgets_reconfigured[self.start_date_entry] = "ui_bg_color_1"

        self.end_date_entry = tb.DateEntry(self.frame, bootstyle=self.ui_settings.ui_bg_color_1, dateformat="%Y-%m-%d")
        self.end_date_entry.bind(
            "<FocusOut>", lambda event: self.__update_date_var(event, self.end_date_entry, "datte_0_02")
        )
        self.__widgets_reconfigured[self.end_date_entry] = "ui_bg_color_1"

    def __update_date_var(self, event, date_entry: tb.DateEntry, date_key: str):
        """ """
        date = date_entry.entry.get()
        self.ui_inp_vars[date_key].tk_var.set(date)  # type: ignore

    def ui(self):
        """ """
        self.gnrl_btns_ui.file_menu_btn(self.__parent_navbar_frame)
        self.site_info_frame()
