import logging
import sys
import threading
import time
from tkinter import messagebox

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
from rss_islandr.ui.btns_change_colour import BtnsChangeColour
from rss_islandr.ui.custom_themes import CustomThemes
from rss_islandr.ui.general_ui import frame_distances
from rss_islandr.ui.home_ui import HomeUI
from rss_islandr.ui.horizontal_navbar import HorizontalNavbar
from rss_islandr.ui.map_ui import MapUI
from rss_islandr.ui.site_info_ui import SiteInfoUI
from rss_islandr.ui.site_to_site_assessment_ui import SiteToSiteAssessmentUI

logging.basicConfig(level=logging.INFO)


class MainAppUI:
    """Implementation of main UI"""

    def __init__(self, root: tb.Window):
        """ """
        self.root = root
        self.ui_settings = read_skin_details(settings, "dark")
        self.theme = self.ui_settings.ui_ttkbootstrap_theme
        self.map_polygons_tb = tb.StringVar(value="")
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

        self.__init__frame_families()
        self.__init__lat_lng_vars()
        self.__init__populate_frame_infos_dict()
        self.__init__handle_geometry()

        self.map_open = True
        self.map_ui = MapUI(MAP_DIR, tb_style, self.ui_inp_vars, self.map_polygons_tb)

        self.__islandr_logo_img = Image.open(ISLANDR_LOGO)
        self.__islandr_logo_img = self.__islandr_logo_img.convert("RGBA")
        self.__islandr_logo_img = ImageTk.PhotoImage(self.__islandr_logo_img)

        # Store references to navigation buttons - used for restyling buttons when pressed
        self.__nav_buttons_references = {}

    def __init__frame_families(self):
        """Definition of frame aliases"""
        self.__scenario_ids = ["on-on", "on-off", "off-on"]
        self.__frame_families = {
            "source_frame": [
                f"{inp}_{scenario_id}_frame" for inp in self.__source_keys for scenario_id in self.__scenario_ids
            ],
            "pathway_frames": [
                f"{inp}_{scenario_id}_frame" for inp in self.__pathway_keys for scenario_id in self.__scenario_ids
            ],
            "receptor_frames": [
                f"{inp}_{scenario_id}_frame" for inp in self.__receptor_keys for scenario_id in self.__scenario_ids
            ],
            "risk_frames": [
                f"{inp}_{scenario_id}_frame_risk" for inp in self.__all_keys for scenario_id in self.__scenario_ids
            ],
        }

    def __init__lat_lng_vars(self):
        """Definition of langtitude and longtitude variables which are updated from the map app."""

        crs = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=tb.StringVar(value=None),
            rel_pos=1,
            text_val="CRS",
            val_default="",
            text_descr=None,
            excel_cell="C4",
        )

        lat = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=tb.StringVar(value=None),
            rel_pos=2,
            text_val="Latitude",
            val_default="",
            text_descr=None,
            excel_cell="C5",
        )

        lng = UIInpVariable(
            frame_tag="site_info_frame",
            tk_var=tb.StringVar(value=None),
            rel_pos=2,
            text_val="Longitude",
            val_default="",
            text_descr=None,
            excel_cell="D5",
        )

        self.ui_inp_vars.update({"map_0_00": crs, "map_0_01": lat, "map_0_02": lng})

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

    def __create_home_btn(self, nav_bar_frame: tb.Frame) -> tb.Button:
        """ """
        btn_home = tb.Button(
            nav_bar_frame,
            text="Home Page",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(self.__home_page, "home"),
        )
        btn_home.grid(row=0, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_home] = "ui_btn_bg_color_1"

        return btn_home

    def __create_map_btn(self, nav_bar_frame: tb.Frame) -> None:
        """ """
        self.btn_map = tb.Button(
            nav_bar_frame,
            text="Maps Viewer",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=self.__toggle_map,
        )
        self.btn_map.grid(row=1, column=0, sticky="nsew")
        self.widgets_reconfigured[self.btn_map] = "ui_btn_bg_color_1"

    def __create_site_info_btn(self, nav_bar_frame: tb.Frame) -> tb.Button:
        """ """
        btn_site_info = tb.Button(
            nav_bar_frame,
            text="Site info",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(self.__site_info_page, "site_info"),
        )
        btn_site_info.grid(row=2, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_site_info] = "ui_btn_bg_color_1"

        return btn_site_info

    def __create_on_site_on_site_btn(self, nav_bar_frame: tb.Frame) -> tb.Button:
        """ """
        btn_on_site_on_site = tb.Button(
            nav_bar_frame,
            text="On-site to on-site",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(self.__site_to_site_page, "on_site_on_site"),
        )
        btn_on_site_on_site.grid(row=3, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_on_site_on_site] = "ui_btn_bg_color_1"

        return btn_on_site_on_site

    def __create_on_site_off_site_btn(self, nav_bar_frame: tb.Frame) -> tb.Button:
        """ """
        btn_on_site_off_site = tb.Button(
            nav_bar_frame,
            text="On-site to off-site",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(self.__site_to_off_site_page, "on_site_off_site"),
        )
        btn_on_site_off_site.grid(row=4, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_on_site_off_site] = "ui_btn_bg_color_1"

        return btn_on_site_off_site

    def __create_off_site_on_site_btn(self, nav_bar_frame: tb.Frame) -> tb.Button:
        """ """
        btn_off_site_on_site = tb.Button(
            nav_bar_frame,
            text="Off-site to on-site",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(self.__off_site_to_site_page, "off_site_on_site"),
        )
        btn_off_site_on_site.grid(row=5, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_off_site_on_site] = "ui_btn_bg_color_1"

        return btn_off_site_on_site

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
            self.ui_inp_vars.get("map_0_01").tk_var.set(None)  # Reset latitude
            self.ui_inp_vars.get("map_0_02").tk_var.set(None)  # Reset longitude
            self.ui_inp_vars.get("map_0_00").tk_var.set(None)  # Reset longitude
            self.map_polygons_tb.set("")  # Clear polygons
            self.map_ui.update_coordinates()
            self.map_ui.update_polygons_from_stringvar()
            for tk_var_tag in self.ui_inp_vars:
                val_default = self.ui_inp_vars[tk_var_tag].val_default
                self.ui_inp_vars[tk_var_tag].tk_var.set(val_default)
            messagebox.showinfo("Success", "Values restored!")
        else:
            pass

    def __toggle_map(self):
        self.map_ui.run_webview()
        self.btn_map.config(text="Maps Viewer")
        #: Start a thread to check for coordinate updates in the webview app.
        threading.Thread(target=self.__monitor_map_changes, daemon=True).start()

    def __monitor_map_changes(self):
        """Continuously checks for new coordinates from MapUI when the map is open."""
        logging.debug(f"{self.__monitor_map_changes.__name__} called!")
        while self.map_open:
            coords = self.map_ui.get_coordinates()
            if coords is not None:
                lat, lng, crs = coords
                self.__update_coordinates(lat, lng, crs)

            if self.map_polygons_tb.get() == "":
                map_polygons_as_str = self.map_ui.get_polygons_data()
            else:
                map_polygons_as_str = self.map_polygons_tb.get()

            self.__update_polygons_data(map_polygons_as_str)

            time.sleep(0.5)  # Polling interval (s) If commented out the main page cannot close

    def __update_coordinates(self, lat, lng, crs) -> None:
        """Callback function to update the coordinates"""
        self.ui_inp_vars["map_0_01"].tk_var.set(lat)
        self.ui_inp_vars["map_0_02"].tk_var.set(lng)
        self.ui_inp_vars["map_0_00"].tk_var.set(crs)
        logging.info(f"Updated Coordinates: {lat}, {lng}, {crs}")

    def __update_polygons_data(self, map_polygons_as_str: str) -> None:
        """Callback function to update polygons data"""
        self.map_polygons_tb.set(map_polygons_as_str)
        logging.debug(f"Updated polygons: {map_polygons_as_str}")

    def __create_vertical_navbar_buttons(self) -> None:
        """
        Create vertical navbar buttons
        """
        nav_bar_frame = self.__create_vertical_navbar()
        self.__nav_buttons_references["home"] = self.__create_home_btn(nav_bar_frame)
        self.__create_map_btn(nav_bar_frame)
        self.__nav_buttons_references["site_info"] = self.__create_site_info_btn(nav_bar_frame)
        self.__nav_buttons_references["on_site_on_site"] = self.__create_on_site_on_site_btn(nav_bar_frame)
        self.__nav_buttons_references["on_site_off_site"] = self.__create_on_site_off_site_btn(nav_bar_frame)
        self.__nav_buttons_references["off_site_on_site"] = self.__create_off_site_on_site_btn(nav_bar_frame)
        self.__create_restore_vars_btn(nav_bar_frame)

    def __create_assessment_apps(self) -> list[SiteToSiteAssessmentUI]:
        """
        Create contamination assessment objects that handle the following 3 cases.
            1. On-site to on-site
            2. On-site to off-site
            3. Off-site to on-site
        """
        site_to_site_apps = []
        for page in [self.__site_to_site_page, self.__site_to_off_site_page, self.__off_site_to_site_page]:
            app_navbar_frame, app_frame = HorizontalNavbar(
                self.ui_settings,
                self.ui_inp_vars,
                self.ui_calc_vars,
                self.widgets_reconfigured,
            )(
                page,
                map_polygons_tb=self.map_polygons_tb,
                map_ui=self.map_ui,  # Pass the map_ui instance to HorizontalNavbar
            )

            site_to_site_app = SiteToSiteAssessmentUI(
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
            site_to_site_apps.append(site_to_site_app)

        return site_to_site_apps

    def create_ui(self) -> None:
        """ """
        self.__create_vertical_navbar_buttons()
        self.__btns_cc = BtnsChangeColour(self.ui_settings, self.__nav_buttons_references)

        #: Create pages (frames) for each main page
        self.__map_page = tb.Frame(self.root)
        self.__home_page = tb.Frame(self.root)
        self.__site_info_page = tb.Frame(self.root)
        self.__site_to_site_page = tb.Frame(self.root)
        self.__site_to_off_site_page = tb.Frame(self.root)
        self.__off_site_to_site_page = tb.Frame(self.root)

        for self.page in [
            self.__map_page,
            self.__home_page,
            self.__site_info_page,
            self.__site_to_site_page,
            self.__site_to_off_site_page,
            self.__off_site_to_site_page,
        ]:
            self.page.place(
                relx=self.__frames_xstart,
                rely=0,
                relwidth=self.__frames_width,
                relheight=1.0,
            )

        #: Home app Create horizontal navbar and rest of frame per page to be displayed
        home_navbar_frame, home_frame = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__home_page, map_polygons_tb=self.map_polygons_tb, map_ui=self.map_ui)
        app_home = HomeUI(home_navbar_frame, home_frame)

        #: Site info app Create horizontal navbar and rest of frame per page to be displayed
        site_info_navbar_frame, site_info_frame = HorizontalNavbar(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.widgets_reconfigured,
        )(self.__site_info_page, map_polygons_tb=self.map_polygons_tb, map_ui=self.map_ui)
        app_site_info = SiteInfoUI(
            site_info_navbar_frame,
            site_info_frame,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.frame_geometry_dict,
            self.widgets_reconfigured,
        )
        #: Site to site contamination assessment apps.
        site_to_site_apps = self.__create_assessment_apps()

        #: Call ui method of created apps
        app_home.ui(self.__islandr_logo_img)
        app_site_info.ui()
        for scenario_id, site_to_site_app in zip(self.__scenario_ids, site_to_site_apps):
            site_to_site_app.ui(scenario_id)

        self.__btns_cc.show_page(self.__home_page, "home")

    def on_closing(self):
        """Cleaning up resources"""
        self.root.destroy()
        sys.exit()
