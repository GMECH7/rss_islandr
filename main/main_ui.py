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
from rss_islandr.core.datatypes import FramePlacing, UIVariable
from rss_islandr.ui.assessment_ui import AssessmentUI
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

        self.frame_n_rows = 1
        self.frame_n_cols = 2
        self.root.geometry("%dx%d+%d+%d" % (self.main_view_width, self.main_view_height, 10, 10))

        self.ui_inp_vars = {}  # this will be updated
        self.ui_calc_vars = {}  # this will be updated

        self.frame_infos_dict = {"0": {}, "1": {}}
        self.__init__populate_frame_infos_dict()

    def __init__populate_frame_infos_dict(self):

        for btn_key in uis_frame_info:
            for frame_key in uis_frame_info[btn_key]:
                frame_info = uis_frame_info[btn_key][frame_key]
                try:
                    x_l = frame_info.get("x_l")
                    x_r = frame_info.get("x_r")
                    y_u = frame_info.get("y_u")
                    y_d = frame_info.get("y_d")
                    n_row = frame_info.get("n_row", None)
                    n_col = frame_info.get("n_col", None)
                    frame_place = FramePlacing(x_l, x_r, y_u, y_d, n_row, n_col)
                    self.frame_infos_dict[btn_key].update({frame_key: frame_place})
                except Exception:
                    pass

    def __window_creator_template(self, idx: int):
        """ """
        ui_selector: dict[int, Type] = {0: SiteInfoUI, 1: AssessmentUI}
        canvas_specs = [
            self.ui_height,
            self.ui_width,
            self.uis_canvas_names[str(idx)][1],
        ]
        popup = tk.Toplevel()
        popup.geometry(
            "%dx%d+%d+%d" % (self.ui_width, self.ui_height, 10, 50 + self.main_view_height)
        )
        popup.resizable(width=False, height=False)

        application = ui_selector[idx](
            self.ui_inp_vars,
            self.ui_settings,
            PACKAGE_DIR,
            popup,
            canvas_specs,
            self.frame_infos_dict,
        )
        application.ui()

        return None

    def on_closing(self):
        """
        By pressing the main x button Tkinter window closes and exits the program
        """
        self.root.destroy()  # Close the Tkinter window
        sys.exit()  # Exit the program completely

    def __frame_distances(self, frame) -> None:
        """ """
        for i in range(self.frame_n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(self.frame_n_cols):
            frame.grid_columnconfigure(i, weight=1)
        return None

    def create_ui(self) -> None:
        """
        Main UI creator.
        """
        canvas = tk.Canvas(
            self.root,
            height=self.main_view_height,
            width=self.main_view_width,
            bg=self.ui_settings.ui_bg_color_1,
        )
        canvas.pack(side="top", fill="both", expand=True)

        frame = tk.Frame(self.root)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.__frame_distances(frame)

        button1 = tk.Button(
            frame,
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            text=self.uis_canvas_names[str(0)][0],
            command=lambda: self.__window_creator_template(0),
        )
        button1.grid(row=0, column=0, sticky="nsew")

        button2 = tk.Button(
            frame,
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            text=self.uis_canvas_names[str(1)][0],
            command=lambda: self.__window_creator_template(1),
        )
        button2.grid(row=0, column=1, sticky="nsew")

        return None


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
