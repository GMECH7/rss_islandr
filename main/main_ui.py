import json
import sys
import tkinter as tk
from typing import Type

from main_imports import PACKAGE_DIR

from rss_islandr.core.config_parser import (
    ui_bg_color_1,
    ui_font_color_1,
    ui_heights,
    ui_widths,
    uis_canvas_names,
    uis_frame_info,
)
from rss_islandr.ui.site_info_ui import SiteInfoUI


class RSSUI:
    """Implementation of main UI"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.background_color = ui_bg_color_1
        self.button_color = ui_bg_color_1
        self.button_font_color = ui_font_color_1
        self.main_view_height = ui_heights[0]
        self.main_view_width = ui_widths[0]
        self.ui_height = ui_heights[1]
        self.ui_width = ui_widths[1]
        self.uis_canvas_names = uis_canvas_names
        self.frame_n_rows = 1
        self.frame_n_cols = 2
        self.root.geometry("%dx%d+%d+%d" % (self.main_view_width, self.main_view_height, 10, 10))

    def __window_creator_template(self, idx: int):
        """ """
        ui_selector: dict[int, Type] = {
            0: SiteInfoUI,
        }
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
            PACKAGE_DIR,
            popup,
            canvas_specs,
            uis_frame_info[str(idx)],
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
            bg=self.background_color,
        )
        canvas.pack(side="top", fill="both", expand=True)

        frame = tk.Frame(self.root)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.__frame_distances(frame)

        button1 = tk.Button(
            frame,
            bg=self.button_color,
            fg=self.button_font_color,
            text=self.uis_canvas_names[str(0)][0],
            command=lambda: self.__window_creator_template(0),
        )
        button1.grid(row=0, column=0, sticky="NSEW")

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
