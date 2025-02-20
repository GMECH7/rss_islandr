import sys
import tkinter as tk
from tkinter import ttk
from typing import Type

from main_imports import PACKAGE_DIR

from rss_islandr.core.config_parser import (
    ICO_DIR,
    MAP_DIR,
    ui_heights,
    ui_settings,
    ui_widths,
    uis_canvas_names,
    uis_frame_geometry,
)
from rss_islandr.core.datatypes import FramePlacing
from rss_islandr.ui.assessment_notebook_ui import AssessmentNoteBookUI
from rss_islandr.ui.excel_writer_btn_ui import ExcelWriterBtnUI
from rss_islandr.ui.map_ui import MapUI
from rss_islandr.ui.site_info_ui import SiteInfoUI


class RSSUI:
    """Implementation of main UI"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.ui_settings = ui_settings

        self.main_view_height = ui_heights[0]
        self.main_view_width = ui_widths[0]
        self.ui_height = ui_heights[1]
        self.ui_width = ui_widths[1]
        self.uis_canvas_names = uis_canvas_names

        self.frame_n_rows = 7
        self.frame_n_cols = 1
        self.root.geometry("%dx%d+%d+%d" % (self.main_view_width, self.main_view_height, 10, 10))

        self.ui_inp_vars = {}  # this will be updated
        self.ui_calc_vars = {}  # this will be updated
        self.frame_geometry_dict = {}

        self.excel_file_template = PACKAGE_DIR / "templates/results.xlsx"

        self.map_ui = MapUI(MAP_DIR)
        self.__source_keys = ["IN"]
        self.__pathway_keys = ["SL", "GW", "SW", "AR", "SD"]
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
                x_l: float = frame_info.get("x_l", 0.0)
                x_r: float = frame_info.get("x_r", 1.0)
                y_u: float = frame_info.get("y_u", 0.0)
                y_d: float = frame_info.get("y_d", 1.0)
                n_row: int = frame_info.get("n_row", 1)
                n_col: int = frame_info.get("n_col", 1)

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
        """ """
        for i in range(self.frame_n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(self.frame_n_cols):
            frame.grid_columnconfigure(i, weight=1)
        return None

    def create_ui(self) -> None:
        """
        Creates a navigation ribbon and main content area with multiple pages.
        """
        # Navigation Ribbon (Fixed for entire program lifetime)
        nav_bar_frame = tk.Frame(self.root, bg=self.ui_settings.ui_bg_color_2)
        nav_bar_frame.place(relx=0, rely=0, relwidth=0.10, relheight=1.0)
        self.frame_distances(nav_bar_frame)

        # # Buttons for navigation
        btn_site_info = tk.Button(
            nav_bar_frame,
            text=self.uis_canvas_names[str(0)][0],
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.site_info_page),
        )
        btn_site_info.grid(row=0, column=0, sticky="nsew")

        # button2 = tk.Button(
        #     nav_bar_frame,
        #     text=self.uis_canvas_names[str(1)][0],
        #     bg=self.ui_settings.ui_btn_bg_color_1,
        #     fg=self.ui_settings.ui_btn_font_color_1,
        #     command=lambda: self.show_page(self.map_page),
        # )

        # button2.grid(row=1, column=0, sticky="nsew")

        excel_writer = ExcelWriterBtnUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.excel_file_template,
        )

        # Button to toggle the map
        self.btn_map = tk.Button(
            nav_bar_frame,
            text="Show Map",
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=self.toggle_map,
        )
        self.btn_map.grid(row=1, column=0, sticky="nsew")

        btn_source = tk.Button(
            nav_bar_frame,
            text="Source",
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.source_page),
        )
        btn_source.grid(row=2, column=0, sticky="nsew")

        btn_pathways = tk.Button(
            nav_bar_frame,
            text="Pathways",
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.pathways_page),
        )
        btn_pathways.grid(row=3, column=0, sticky="nsew")

        btn_receptors = tk.Button(
            nav_bar_frame,
            text="Receptors",
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.receptors_page),
        )
        btn_receptors.grid(row=4, column=0, sticky="nsew")

        btn_xlsx_writer = excel_writer.button(nav_bar_frame)
        btn_xlsx_writer.grid(row=6, column=0, sticky="nsew")

        # Create Pages
        self.site_info_page = tk.Frame(self.root)
        self.map_page = tk.Frame(self.root)
        self.source_page = tk.Frame(self.root)
        self.pathways_page = tk.Frame(self.root)
        self.receptors_page = tk.Frame(self.root)

        for self.page in [
            self.site_info_page,
            self.map_page,
            self.source_page,
            self.pathways_page,
            self.receptors_page,
        ]:
            self.page.place(relx=0.105, rely=0, relwidth=0.895, relheight=1.0)

        # Initialize pages
        canvas_specs = [
            self.ui_height,
            self.ui_width,
            self.uis_canvas_names[str(0)][1],
        ]

        application = SiteInfoUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.site_info_page,
            canvas_specs,
            self.frame_geometry_dict,
        )
        self.__window_creator_template(0, application, self.site_info_page)

        canvas_specs = [
            self.ui_height,
            self.ui_width,
            self.uis_canvas_names[str(1)][1],
        ]

        application2 = AssessmentNoteBookUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.source_page,
            canvas_specs,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
        )
        self.__window_creator_template(1, application2, self.source_page)
        self.__window_creator_template(2, application2, self.pathways_page)
        self.__window_creator_template(
            3,
            application2,
            self.receptors_page,
        )

        # Show the first page by default
        self.show_page(self.site_info_page)

    def __window_creator_template(self, idx: int, application, frame):
        """
        Creates UI elements for each page.
        """
        # ui_selector: dict[int, Type] = {
        #     0: SiteInfoUI,
        #     1: AssessmentNoteBookUI,
        #     2: AssessmentNoteBookUI,
        #     3: AssessmentNoteBookUI,
        # }
        # canvas_specs = [
        #     self.ui_height,
        #     self.ui_width,
        #     self.uis_canvas_names[str(idx)][1],
        # ]

        # application = ui_selector[idx](
        #     self.ui_settings,
        #     self.ui_inp_vars,
        #     self.ui_calc_vars,
        #     parent_frame,
        #     canvas_specs,
        #     self.frame_geometry_dict,
        # )
        if idx == 1:
            application.ui(frame, "source")
        elif idx == 2:
            application.ui(frame, "pathways")
        elif idx == 3:
            application.ui(frame, "receptors")
        else:
            application.ui()

    def show_page(self, page):
        """Brings the given page to the front."""
        page.tkraise()

    def toggle_map(self):
        if self.map_open:
            # If the map is open, close it
            self.map_ui.close_map()
            self.map_open = False
            self.btn_map.config(text="Show Map")
        else:
            # If the map is closed, show it
            self.map_ui.show_map()
            self.map_open = True
            self.btn_map.config(text="Close Map")

    def on_closing(self):
        """
        By pressing the main x button Tkinter window closes and exits the program
        """
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("RSS-ISLANDR")
    root.iconbitmap(ICO_DIR)
    main = RSSUI(root)
    main.create_ui()
    #: Set the protocol to handle the window close button
    root.protocol("WM_DELETE_WINDOW", main.on_closing)
    root.mainloop()
