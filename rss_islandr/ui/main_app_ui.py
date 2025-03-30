import logging
import sys
import threading
import time

import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.dialogs import Messagebox

from rss_islandr.core.config_parser import (
    ISLANDR_LOGO,
    MAP_DIR,
    pathway_keys,
    settings,
    source_keys,
    ui_heights,
    ui_widths,
    uis_frame_geometry,
)
from rss_islandr.core.datatypes import FramePlacing, UIInpVariable
from rss_islandr.core.skin_reader import read_skin_details
from rss_islandr.ui.app_ui import AppUI
from rss_islandr.ui.assessment_notebook_ui import AssessmentNoteBookUI
from rss_islandr.ui.custom_themes import CustomThemes
from rss_islandr.ui.general_ui import frame_distances
from rss_islandr.ui.home_ui import HomeUI
from rss_islandr.ui.horizontal_navbar import HorizontalNavbar
from rss_islandr.ui.io_btns import ExportExcelReportBtn, ExportScenarioBtn, ImportScenarioBtn
from rss_islandr.ui.map_ui import MapUI
from rss_islandr.ui.site_info_ui import SiteInfoUI

logging.basicConfig(level=logging.INFO)


class MainAppUI:
    """Implementation of main UI"""

    def __init__(self, root: tb.Window):
        """ """
        self.root = root
        self.ui_settings = read_skin_details(settings, "dark")
        self.theme = self.ui_settings.ui_ttkbootstrap_theme
        tb_style = tb.Style(self.theme)
        #: Create custom themes
        ct = CustomThemes(tb_style, self.ui_settings)
        ct()

        self.ui_inp_vars = {}
        self.ui_calc_vars = {}
        self.meter_frames = {}
        self.frame_geometry_dict = {}
        self.widgets_reconfigured = {}
        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = [f"{pathway}_receptor" for pathway in self.__pathway_keys]
        self.__all_keys = self.__source_keys + self.__pathway_keys + self.__receptor_keys
        self.__frame_families = {
            "source_frame": [f"{inp}_{scenario_id}_frame" for inp in self.__source_keys for scenario_id in [1, 2, 3]],
            "pathway_frames": [
                f"{inp}_{scenario_id}_frame" for inp in self.__pathway_keys for scenario_id in [1, 2, 3]
            ],
            "receptor_frames": [
                f"{inp}_{scenario_id}_frame" for inp in self.__receptor_keys for scenario_id in [1, 2, 3]
            ],
            "risk_frames": [f"{inp}_{scenario_id}_frame_risk" for inp in self.__all_keys for scenario_id in [1, 2, 3]],
        }
        self.__init__lat_lng_vars()
        self.__init__populate_frame_infos_dict()
        self.__init__handle_geometry()

        self.map_open = True
        self.map_ui = MapUI(MAP_DIR, tb_style, self.__map_height, self.__map_width)

        self.__islandr_logo_img = Image.open(ISLANDR_LOGO)
        self.__islandr_logo_img = self.__islandr_logo_img.convert("RGBA")
        self.__islandr_logo_img = ImageTk.PhotoImage(self.__islandr_logo_img)

    def __init__lat_lng_vars(self):
        """Definition of langtitude and longtitude variables which are updated from the map app."""

        lat = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=tb.StringVar(value="0.0"),
            rel_pos=1,
            text_val="Latitude",
            val_default="0.0",
            text_descr=None,
            excel_cell="C4",
        )

        lng = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=tb.StringVar(value="0.0"),
            rel_pos=1,
            text_val="Longtitude",
            val_default="0.0",
            text_descr=None,
            excel_cell="D4",
        )

        self.ui_inp_vars.update({"map_0_00": lat, "map_0_01": lng})

    def __init__populate_frame_infos_dict(self):
        """ """
        for frame_key in uis_frame_geometry:
            frame_info = uis_frame_geometry[frame_key]
            try:
                x_l = frame_info.get("x_l", 0.0)
                x_r = frame_info.get("x_r", 1.0)
                y_u = frame_info.get("y_u", 0.0)
                y_d = frame_info.get("y_d", 1.0)
                #: the number of rows is updated in code
                n_row = frame_info.get("n_row", 1)
                if frame_key == "risk_frames":
                    n_cols_default = 1
                elif frame_key == "site_info_frame":
                    n_cols_default = 3
                else:
                    n_cols_default = 2

                #: the number of columns are by default 2 (1 label left 1 widget right)
                n_col = frame_info.get("n_col", n_cols_default)
                if frame_key in self.__frame_families:
                    for frame_key_specific in self.__frame_families[frame_key]:
                        frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                        self.frame_geometry_dict.update({frame_key_specific: frame_place})
                else:
                    frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                    self.frame_geometry_dict.update({frame_key: frame_place})
            except Exception:
                pass

    def __init__handle_geometry(self):
        """ """
        self.__main_view_height = ui_heights[0]
        self.__main_view_width = ui_widths[0]
        self.__map_height = ui_heights[1]
        self.__map_width = ui_widths[1]
        self.__frame_n_rows = self.frame_geometry_dict["vertical_navbar_frame"].n_row
        self.__frame_n_cols = self.frame_geometry_dict["vertical_navbar_frame"].n_col
        self.__navbar_width = 0.1
        self.__navbar_padx = 0.005
        self.__frames_xstart = self.__navbar_width + self.__navbar_padx
        self.__frames_width = 1.0 - self.__navbar_padx - self.__navbar_width
        self.root.geometry("%dx%d+%d+%d" % (self.__main_view_width, self.__main_view_height, 10, 10))

    def __create_vertical_navbar(self) -> tb.Frame:
        """Create vertical navbar visible in all app."""
        nav_bar_frame = tb.Frame(self.root)
        nav_bar_frame.place(relx=0, rely=0, relwidth=self.__navbar_width, relheight=1.0)
        frame_distances(nav_bar_frame, self.__frame_n_rows, self.__frame_n_cols)
        nav_bar_pad_frame = tb.Frame(self.root, style="NavbarPad.TFrame")
        nav_bar_pad_frame.place(relx=self.__navbar_width, rely=0, relwidth=self.__navbar_padx, relheight=1.0)
        return nav_bar_frame

    def __create_home_btn(self, nav_bar_frame: tb.Frame):
        """ """
        btn_home = tb.Button(
            nav_bar_frame,
            text="Home Page",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(self.__home_page),
        )
        btn_home.grid(row=0, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_home] = "ui_btn_bg_color_1"

    def __create_map_btn(self, nav_bar_frame: tb.Frame) -> None:
        """ """
        self.btn_map = tb.Button(
            nav_bar_frame,
            text="Show Map",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=self.__toggle_map,
        )
        self.btn_map.grid(row=1, column=0, sticky="nsew")
        self.widgets_reconfigured[self.btn_map] = "ui_btn_bg_color_1"

    def __create_site_info_btn(self, nav_bar_frame: tb.Frame):
        """ """
        btn_site_info = tb.Button(
            nav_bar_frame,
            text="Site info",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(self.__site_info_page),
        )
        btn_site_info.grid(row=2, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_site_info] = "ui_btn_bg_color_1"

    def __create_site_to_site_btn(self, nav_bar_frame: tb.Frame):
        """ """
        btn_site_to_site = tb.Button(
            nav_bar_frame,
            text="Site to site Assessment",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(self.__site_to_site_page),
        )
        btn_site_to_site.grid(row=3, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_site_to_site] = "ui_btn_bg_color_1"

    def __create_site_to_off_site_btn(self, nav_bar_frame: tb.Frame):
        """ """
        btn_site_to_site = tb.Button(
            nav_bar_frame,
            text="Site to off site assessment",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(self.__site_to_off_site_page),
        )
        btn_site_to_site.grid(row=4, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_site_to_site] = "ui_btn_bg_color_1"

    def __create_off_site_to_site_btn(self, nav_bar_frame: tb.Frame):
        """ """
        btn_site_to_site = tb.Button(
            nav_bar_frame,
            text="Off site to site assessment",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(self.__off_site_to_site_page),
        )
        btn_site_to_site.grid(row=5, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_site_to_site] = "ui_btn_bg_color_1"

    # def __create_source_btn(self, nav_bar_frame: tb.Frame) -> None:
    #     """ """
    #     btn_source = tb.Button(
    #         nav_bar_frame,
    #         text="Source",
    #         style=self.ui_settings.ui_btn_bg_color_1,
    #         command=lambda: self.__show_page(self.__source_page),
    #     )
    #     btn_source.grid(row=4, column=0, sticky="nsew")
    #     self.widgets_reconfigured[btn_source] = "ui_btn_bg_color_1"

    # def __create_pathways_btn(self, nav_bar_frame: tb.Frame) -> None:
    #     """ """
    #     btn_pathways = tb.Button(
    #         nav_bar_frame,
    #         text="Pathways",
    #         style=self.ui_settings.ui_btn_bg_color_1,
    #         command=lambda: self.__show_page(self.__pathways_page),
    #     )
    #     btn_pathways.grid(row=5, column=0, sticky="nsew")
    #     self.widgets_reconfigured[btn_pathways] = "ui_btn_bg_color_1"

    # def __create_receptors_btn(self, nav_bar_frame: tb.Frame) -> None:
    #     """ """
    #     btn_receptors = tb.Button(
    #         nav_bar_frame,
    #         text="Receptors",
    #         style=self.ui_settings.ui_btn_bg_color_1,
    #         command=lambda: self.__show_page(self.__receptors_page),
    #     )
    #     btn_receptors.grid(row=6, column=0, sticky="nsew")
    #     self.widgets_reconfigured[btn_receptors] = "ui_btn_bg_color_1"

    def __create_restore_vars_btn(self, frame: tb.Frame) -> tb.Button:
        """Restore to default button"""
        restore_btn = tb.Button(
            frame,
            style="warning",
            text="Restore defaults",
            command=self.__restore_all,
        )
        restore_btn.grid(row=6, column=0, sticky="nsew")

        return restore_btn

    def __restore_all(self) -> None:
        """ """
        result = Messagebox.yesno("Are you sure you want to restore defaults?", "Confirmation")
        if result == "Yes":
            for tk_var_tag in self.ui_inp_vars:
                val_default = self.ui_inp_vars[tk_var_tag].val_default
                self.ui_inp_vars[tk_var_tag].tk_var.set(val_default)
        else:
            pass

    def __create_xlsx_writer_btn(self, nav_bar_frame: tb.Frame) -> None:
        """NOT Used"""
        excel_writer = ExportExcelReportBtn(self.ui_inp_vars, self.ui_calc_vars)
        btn_xlsx_writer = excel_writer.btn(nav_bar_frame)
        btn_xlsx_writer.grid(row=7, column=0, sticky="nsew")

    def __create_scenario_writer_btn(self, nav_bar_frame: tb.Frame) -> None:
        """NOT Used"""
        excel_writer = ExportScenarioBtn(self.ui_inp_vars, self.ui_calc_vars)
        btn_scenario_writer = excel_writer.btn(nav_bar_frame)
        btn_scenario_writer.grid(row=8, column=0, sticky="nsew")

    def __create_scenario_reader_btn(self, nav_bar_frame: tb.Frame) -> None:
        """NOT Used"""
        excel_writer = ImportScenarioBtn(self.ui_inp_vars, self.ui_calc_vars)
        btn_scenario_writer = excel_writer.btn(nav_bar_frame)
        btn_scenario_writer.grid(row=9, column=0, sticky="nsew")

    def __show_page(self, page):
        page.tkraise()

    def __toggle_map(self):
        # if self.map_open:
        #     self.map_ui.close_map()
        #     self.map_open = False
        #     self.btn_map.config(text="Show Map")
        # else:
        #     self.map_ui.run_webview()
        #     # self.map_ui.show_map()
        #     self.map_open = True
        #     self.btn_map.config(text="Show Map")
        self.map_ui.run_webview()
        self.btn_map.config(text="Show Map")
        #: Start a thread to check for coordinate updates in the webview app.
        threading.Thread(target=self.__monitor_coordinates, daemon=True).start()

    def __monitor_coordinates(self):
        """Continuously checks for new coordinates from MapUI when the map is open."""
        logging.info(f"{self.__monitor_coordinates.__name__} called")
        while self.map_open:
            coords = self.map_ui.get_coordinates()
            if coords is not None:
                lat, lng = coords
                self.__update_coordinates(lat, lng)
            time.sleep(1.0)  # Polling interval (s)

    def __update_coordinates(self, lat, lng):
        """Callback function to update the coordinates label."""
        self.ui_inp_vars["map_0_00"].tk_var.set(lat)
        self.ui_inp_vars["map_0_01"].tk_var.set(lng)
        logging.debug(f"Updated Coordinates: {lat}, {lng}")

    def __create_vertical_navbar_buttons(self) -> None:
        """ """

        nav_bar_frame = self.__create_vertical_navbar()
        #: Create vertical navbar buttons
        self.__create_home_btn(nav_bar_frame)
        self.__create_map_btn(nav_bar_frame)
        self.__create_site_info_btn(nav_bar_frame)
        self.__create_site_to_site_btn(nav_bar_frame)
        self.__create_site_to_off_site_btn(nav_bar_frame)
        self.__create_off_site_to_site_btn(nav_bar_frame)
        # self.__create_source_btn(nav_bar_frame)
        # self.__create_pathways_btn(nav_bar_frame)
        # self.__create_receptors_btn(nav_bar_frame)
        self.__create_restore_vars_btn(nav_bar_frame)

    def create_ui(self) -> None:
        """ """
        self.__create_vertical_navbar_buttons()

        #: Create pages (frames) for each main page
        self.__map_page = tb.Frame(self.root)
        self.__home_page = tb.Frame(self.root)
        self.__site_info_page = tb.Frame(self.root)
        self.__site_to_site_page = tb.Frame(self.root)
        self.__site_to_off_site_page = tb.Frame(self.root)
        self.__off_site_to_site_page = tb.Frame(self.root)

        # self.__source_page = tb.Frame(self.root)
        # self.__pathways_page = tb.Frame(self.root)
        # self.__receptors_page = tb.Frame(self.root)

        for self.page in [
            self.__map_page,
            self.__home_page,
            self.__site_info_page,
            self.__site_to_site_page,
            self.__site_to_off_site_page,
            self.__off_site_to_site_page,
            # self.__source_page,
            # self.__pathways_page,
            # self.__receptors_page,
        ]:
            self.page.place(
                relx=self.__frames_xstart,
                rely=0,
                relwidth=self.__frames_width,
                relheight=1.0,
            )
        #: Create horizontal navbar and rest of frame per page to be dispalyed
        home_navbar_frame, home_frame = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__home_page)
        app_home = HomeUI(home_navbar_frame, home_frame)

        site_info_navbar_frame, site_info_frame = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__site_info_page)

        app_site_info = SiteInfoUI(
            site_info_navbar_frame,
            site_info_frame,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.frame_geometry_dict,
            self.widgets_reconfigured,
        )

        app_navbar_frame, app_frame = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__site_to_site_page)

        app_app = AppUI(
            app_navbar_frame,
            app_frame,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.meter_frames,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
            self.widgets_reconfigured,
        )

        app_navbar_frame_2, app_frame_2 = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__site_to_off_site_page)

        app_app_2 = AppUI(
            app_navbar_frame_2,
            app_frame_2,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.meter_frames,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
            self.widgets_reconfigured,
        )

        app_navbar_frame_3, app_frame_3 = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__off_site_to_site_page)

        app_app_3 = AppUI(
            app_navbar_frame_3,
            app_frame_3,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.meter_frames,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
            self.widgets_reconfigured,
        )

        # app_assesment = AssessmentNoteBookUI(
        #     self.ui_settings,
        #     self.ui_inp_vars,
        #     self.ui_calc_vars,
        #     self.meter_frames,
        #     self.frame_geometry_dict,
        #     self.__source_keys,
        #     self.__pathway_keys,
        #     self.__receptor_keys,
        #     widgets_reconfigured=self.widgets_reconfigured,
        # )

        # source_navbar_frame, source_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__source_page)

        # pathways_navbar_frame, pathways_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__pathways_page)

        # receptors_navbar_frame, receptors_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__receptors_page)

        #: Create page
        app_home.ui(self.__islandr_logo_img)
        app_site_info.ui()
        app_app.ui(self.root)
        app_app_2.ui_2(self.root)
        app_app_3.ui_3(self.root)
        # app_app_2.ui(self.root)
        # app_assesment.ui(source_navbar_frame, source_frame, "source")
        # app_assesment.ui(pathways_navbar_frame, pathways_frame, "pathways")
        # app_assesment.ui(receptors_navbar_frame, receptors_frame, "receptors")

        self.__show_page(self.__home_page)

    def on_closing(self):
        """Cleaning up resources"""
        self.root.destroy()
        sys.exit()
