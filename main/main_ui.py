import sys

import ttkbootstrap as tb
from main_imports import PACKAGE_DIR
from ttkbootstrap.constants import PRIMARY, SECONDARY, SUCCESS

from rss_islandr.core.config_parser import (
    ICO_DIR,
    MAP_DIR,
    XLSX_TEMPLATE_FILE,
    app_title,
    pathway_keys,
    source_keys,
    ui_heights,
    ui_settings,
    ui_widths,
    uis_frame_geometry,
)
from rss_islandr.core.datatypes import FramePlacing
from rss_islandr.ui.assessment_notebook_ui import AssessmentNoteBookUI
from rss_islandr.ui.custom_themes import CustomThemes
from rss_islandr.ui.excel_writer_btn_ui import ExcelWriterBtnUI
from rss_islandr.ui.map_ui import MapUI
from rss_islandr.ui.site_info_ui import SiteInfoUI


class RSSUI:
    """Implementation of main UI"""

    def __init__(self, theme: str, root: tb.Window):
        self.root = root
        self.ui_settings = ui_settings
        ct = CustomThemes(theme, ui_settings)
        ct()

        self.main_view_height = ui_heights[0]
        self.main_view_width = ui_widths[0]
        self.ui_height = ui_heights[1]
        self.ui_width = ui_widths[1]

        self.frame_n_rows = 7
        self.frame_n_cols = 1
        self.__navbar_width = 0.1
        self.__navbar_padx = 0.005
        self.__frames_xstart = self.__navbar_width + self.__navbar_padx
        self.__frames_width = 1.0 - self.__navbar_padx - self.__navbar_width
        self.root.geometry("%dx%d+%d+%d" % (self.main_view_width, self.main_view_height, 10, 10))

        self.ui_inp_vars = {}
        self.ui_calc_vars = {}
        self.frame_geometry_dict = {}

        self.excel_file_template = XLSX_TEMPLATE_FILE

        self.map_ui = MapUI(MAP_DIR)
        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = [f"{pathway}_receptor" for pathway in self.__pathway_keys]
        self.__frame_families = {
            "source_frame": [f"{inp}_frame" for inp in self.__source_keys],
            "pathway_frames": [f"{inp}_frame" for inp in self.__pathway_keys],
            "receptor_frames": [f"{inp}_frame" for inp in self.__receptor_keys],
        }
        self.__init__populate_frame_infos_dict()
        self.map_open = False

    def __init__populate_frame_infos_dict(self):
        for frame_key in uis_frame_geometry:
            frame_info = uis_frame_geometry[frame_key]
            try:
                x_l = frame_info.get("x_l", 0.0)
                x_r = frame_info.get("x_r", 1.0)
                y_u = frame_info.get("y_u", 0.0)
                y_d = frame_info.get("y_d", 1.0)
                n_row = frame_info.get("n_row", 1)
                n_col = frame_info.get("n_col", 1)

                if frame_key in self.__frame_families:
                    for frame_key_specific in self.__frame_families[frame_key]:
                        frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                        self.frame_geometry_dict.update({frame_key_specific: frame_place})
                else:
                    frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                    self.frame_geometry_dict.update({frame_key: frame_place})
            except Exception:
                pass

    def frame_distances(self, frame) -> None:
        for i in range(self.frame_n_rows):
            frame.rowconfigure(i, weight=1)
        for i in range(self.frame_n_cols):
            frame.columnconfigure(i, weight=1)

    def __create_navbar(self) -> tb.Frame:
        nav_bar_frame = tb.Frame(self.root)
        nav_bar_frame.place(relx=0, rely=0, relwidth=0.10, relheight=1.0)
        self.frame_distances(nav_bar_frame)
        return nav_bar_frame

    def __create_site_info_btn(self, nav_bar_frame: tb.Frame):
        btn_site_info = tb.Button(
            nav_bar_frame,
            text="Site info",
            command=lambda: self.show_page(self.site_info_page),
        )
        btn_site_info.grid(row=0, column=0, sticky="nsew")

    def __create_map_btn(self, nav_bar_frame: tb.Frame) -> None:
        self.btn_map = tb.Button(
            nav_bar_frame,
            text="Show Map",
            command=self.toggle_map,
        )
        self.btn_map.grid(row=1, column=0, sticky="nsew")

    def __create_source_btn(self, nav_bar_frame: tb.Frame) -> None:
        btn_source = tb.Button(
            nav_bar_frame,
            text="Source",
            command=lambda: self.show_page(self.source_page),
        )
        btn_source.grid(row=2, column=0, sticky="nsew")

    def __create_pathways_btn(self, nav_bar_frame: tb.Frame) -> None:
        btn_pathways = tb.Button(
            nav_bar_frame,
            text="Pathways",
            style="secondary",
            command=lambda: self.show_page(self.pathways_page),
        )
        btn_pathways.grid(row=3, column=0, sticky="nsew")

    def __create_receptors_btn(self, nav_bar_frame: tb.Frame) -> None:
        btn_receptors = tb.Button(
            nav_bar_frame,
            text="Receptors",
            command=lambda: self.show_page(self.receptors_page),
        )
        btn_receptors.grid(row=4, column=0, sticky="nsew")

    def __create_xlsx_writer_btn(self, nav_bar_frame: tb.Frame) -> None:
        excel_writer = ExcelWriterBtnUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.excel_file_template,
        )
        btn_xlsx_writer = excel_writer.button(nav_bar_frame)
        btn_xlsx_writer.grid(row=6, column=0, sticky="nsew")

    def create_ui(self) -> None:
        nav_bar_frame = self.__create_navbar()
        self.__create_site_info_btn(nav_bar_frame)
        self.__create_map_btn(nav_bar_frame)
        self.__create_source_btn(nav_bar_frame)
        self.__create_pathways_btn(nav_bar_frame)
        self.__create_receptors_btn(nav_bar_frame)
        self.__create_xlsx_writer_btn(nav_bar_frame)

        self.site_info_page = tb.Frame(self.root)
        self.map_page = tb.Frame(self.root)
        self.source_page = tb.Frame(self.root)
        self.pathways_page = tb.Frame(self.root)
        self.receptors_page = tb.Frame(self.root)

        for self.page in [
            self.site_info_page,
            self.map_page,
            self.source_page,
            self.pathways_page,
            self.receptors_page,
        ]:
            self.page.place(relx=self.__frames_xstart, rely=0, relwidth=self.__frames_width, relheight=1.0)

        app_site_info = SiteInfoUI(
            self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.site_info_page, self.frame_geometry_dict
        )

        app_assesment = AssessmentNoteBookUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
        )

        app_site_info.ui()
        app_assesment.ui(self.source_page, "source")
        app_assesment.ui(self.pathways_page, "pathways")
        app_assesment.ui(self.receptors_page, "receptors")

        self.show_page(self.site_info_page)

    def show_page(self, page):
        page.tkraise()

    def toggle_map(self):
        if self.map_open:
            self.map_ui.close_map()
            self.map_open = False
            self.btn_map.config(text="Show Map")
        else:
            self.map_ui.run_webview()
            self.map_open = True
            self.btn_map.config(text="Close Map")

    def on_closing(self):
        self.root.destroy()
        sys.exit()


def main():
    theme = "superhero"
    root = tb.Window(themename=theme)
    root.title(app_title)
    root.iconbitmap(ICO_DIR)
    main = RSSUI(theme, root)
    main.create_ui()
    root.protocol("WM_DELETE_WINDOW", main.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
