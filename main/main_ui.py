import sys
import tkinter as tk
from typing import Type

from main_imports import PACKAGE_DIR

from rss_islandr.core.config_parser import (
    ui_heights,
    ui_settings,
    ui_widths,
    uis_canvas_names,
    uis_frame_info,
)
from rss_islandr.core.datatypes import FramePlacing
from rss_islandr.ui.assessment_ui import AssessmentUI
from rss_islandr.ui.excel_writer_btn_ui import ExcelWriterBtnUI
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

        self.frame_n_rows = 5
        self.frame_n_cols = 1
        self.root.geometry("%dx%d+%d+%d" % (self.main_view_width, self.main_view_height, 10, 10))

        self.ui_inp_vars = {}  # this will be updated
        self.ui_calc_vars = {}  # this will be updated

        self.frame_info_dict = {"0": {}, "1": {}}
        self.__init__populate_frame_infos_dict()

        self.excel_file_template = PACKAGE_DIR / "templates/results.xlsx"

    def __init__populate_frame_infos_dict(self):

        for btn_key in uis_frame_info:
            for frame_key in uis_frame_info[btn_key]:
                frame_info = uis_frame_info[btn_key][frame_key]
                try:
                    x_l: float = frame_info.get("x_l", 0.0)
                    x_r: float = frame_info.get("x_r", 1.0)
                    y_u: float = frame_info.get("y_u", 0.0)
                    y_d: float = frame_info.get("y_d", 1.0)
                    n_row: int = frame_info.get("n_row", None)
                    n_col: int = frame_info.get("n_col", None)
                    frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                    self.frame_info_dict[btn_key].update({frame_key: frame_place})
                except Exception:
                    pass

    def __frame_distances(self, frame) -> None:
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
        self.__frame_distances(nav_bar_frame)

        # # Buttons for navigation
        button1 = tk.Button(
            nav_bar_frame,
            text=self.uis_canvas_names[str(0)][0],
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.page1),
        )
        button1.grid(row=0, column=0, sticky="nsew")

        button2 = tk.Button(
            nav_bar_frame,
            text=self.uis_canvas_names[str(1)][0],
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            command=lambda: self.show_page(self.page2),
        )

        button2.grid(row=1, column=0, sticky="nsew")

        excel_writer_btn = ExcelWriterBtnUI(
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.excel_file_template,
        )
        button3 = excel_writer_btn.button(nav_bar_frame)
        button3.grid(row=4, column=0, sticky="nsew")

        # # Create Pages
        self.page1 = tk.Frame(self.root)
        self.page2 = tk.Frame(self.root)

        for page in (self.page1, self.page2):
            page.place(relx=0.1, rely=0, relwidth=0.9, relheight=1.0)

        # Initialize pages
        self.__window_creator_template(0, self.page1)
        self.__window_creator_template(1, self.page2)

        # Show the first page by default
        self.show_page(self.page1)

    def __window_creator_template(self, idx: int, parent_frame):
        """
        Creates UI elements for each page.
        """
        ui_selector: dict[int, Type] = {0: SiteInfoUI, 1: AssessmentUI}
        canvas_specs = [
            self.ui_height,
            self.ui_width,
            self.uis_canvas_names[str(idx)][1],
        ]

        application = ui_selector[idx](
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            PACKAGE_DIR,
            parent_frame,
            canvas_specs,
            self.frame_info_dict,
        )

        application.ui()

    def show_page(self, page):
        """Brings the given page to the front."""
        page.tkraise()

    def on_closing(self):
        """
        By pressing the main x button Tkinter window closes and exits the program
        """
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("RSS-ISLANDR")
    root.iconbitmap(str(PACKAGE_DIR / "static" / "trade.ico"))
    main = RSSUI(root)
    main.create_ui()
    #: Set the protocol to handle the window close button
    root.protocol("WM_DELETE_WINDOW", main.on_closing)
    root.mainloop()
