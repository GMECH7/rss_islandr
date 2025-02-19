# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from rss_islandr.core.datatypes import UIInpVariable, UISettings


class GeneralUITemplate:

    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        root: tk.Toplevel,
        frame_geometry_dict,
        canvas_height,
        canvas_width,
    ):
        """ """
        self.ui_inp_vars = ui_inp_vars
        self.ui_settings = ui_settings
        self.root = root
        self.frame_geometry_dict = frame_geometry_dict
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        self.message_variable = tk.StringVar()

    def __str__(self):
        """ """
        return str(__class__.__name__)

    def frame_distances(self, frame: tk.Frame, n_rows: int, n_cols: int) -> None:
        """ """
        for i in range(n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(n_cols):
            frame.grid_columnconfigure(i, weight=1)

        return None

    def template_title(self, frame_title, rel_x, rel_y, rel_w, rel_h) -> None:
        """ """
        title_frame = tk.Frame(self.root, bg=self.ui_settings.ui_bg_color_1)
        title_frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)
        self.frame_distances(title_frame, 0, 1)
        title_label = tk.Label(
            title_frame,
            text=frame_title,
            bg=self.ui_settings.ui_bg_color_2,
            fg=self.ui_settings.ui_title_font_color,
            relief="raised",
            justify="center",
        )
        title_label.grid(row=0, column=0, sticky="nsew")
        title_label.config(
            font=(self.ui_settings.ui_title_font_type, self.ui_settings.ui_font_size)
        )

        return None

    def frame_limits(self, frame_tag: str) -> tuple:
        """ """
        rel_x = self.frame_geometry_dict[frame_tag].x_l
        x_r = self.frame_geometry_dict[frame_tag].x_r

        rel_y = self.frame_geometry_dict[frame_tag].y_u
        y_d = self.frame_geometry_dict[frame_tag].y_d

        rel_w = x_r - rel_x
        rel_h = y_d - rel_y

        n_rows = self.frame_geometry_dict[frame_tag].n_row
        n_cols = self.frame_geometry_dict[frame_tag].n_col
        print(frame_tag, self.frame_geometry_dict[frame_tag])
        return rel_x, rel_y, rel_w, rel_h, n_rows, n_cols

    def bb(self, frame, frame_title, rel_x, rel_y, rel_w, rel_h) -> None:
        """ """
        title_frame = tk.Frame(frame, bg=self.ui_settings.ui_bg_color_1)
        title_frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)
        self.frame_distances(title_frame, 0, 1)
        title_label = tk.Label(
            title_frame,
            text=frame_title,
            bg=self.ui_settings.ui_bg_color_2,
            fg=self.ui_settings.ui_title_font_color,
            relief="raised",
            justify="center",
        )
        title_label.grid(row=0, column=0, sticky="nsew")
        title_label.config(
            font=(self.ui_settings.ui_title_font_type, self.ui_settings.ui_font_size)
        )

        return None

    def aa(self, frame, frame_tag: str, frame_title: str):
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        self.bb(frame, frame_title, rel_x, rel_y, rel_w, rel_h)
        title_offset = 0.0 if frame_title == "" else self.ui_settings.ui_title_offset
        frame = tk.Frame(frame, bg=self.ui_settings.ui_bg_color_1)
        frame.place(
            relx=rel_x,
            rely=rel_y + title_offset,
            relwidth=rel_w,
            relheight=rel_h - title_offset,
        )
        self.frame_distances(frame, n_rows, n_cols)

        return frame

    def general_template_frames(self, frame_tag: str, frame_title: str) -> tk.Frame:
        """ """
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        self.template_title(frame_title, rel_x, rel_y, rel_w, rel_h)
        title_offset = 0.0 if frame_title == "" else self.ui_settings.ui_title_offset

        frame = tk.Frame(self.root, bg=self.ui_settings.ui_bg_color_1)
        frame.place(
            relx=rel_x,
            rely=rel_y + title_offset,
            relwidth=rel_w,
            relheight=rel_h - title_offset,
        )
        self.frame_distances(frame, n_rows, n_cols)

        return frame

    def general_template_entries(self, frame: tk.Frame, entry_key: str) -> None:

        label = tk.Label(
            frame,
            text=self.ui_inp_vars[entry_key].text_val,
            bg=self.ui_settings.ui_bg_color_2,
            fg=self.ui_settings.ui_font_color_1,
            relief="raised",
        )

        label.grid(
            row=self.ui_inp_vars[entry_key].rel_pos,
            column=0,
            sticky="nsew",
        )

        label.config(font=(self.ui_settings.ui_title_font_type, self.ui_settings.ui_font_size))

        entry = tk.Entry(
            frame,
            textvariable=self.ui_inp_vars[entry_key].tk_var,
            bg=self.ui_settings.ui_bg_color_2,
            fg=self.ui_settings.ui_font_color_1,
            relief="raised",
            justify="center",
        )

        entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, sticky="nsew")
        entry.config(font=(self.ui_settings.ui_title_font_type, self.ui_settings.ui_font_size))

        return None

    def general_template_dropdown(self, frame: tk.Frame, dropdown_key: str) -> None:
        """
        General template used to create a dropdown widget.

        Parameters
        ----------
        frame : tk.Frame
            _description_
        dropdown_key : str
            _description_
        """

        label = tk.Label(
            frame,
            text=self.ui_inp_vars[dropdown_key].text_val,
            bg=self.ui_settings.ui_bg_color_2,
            fg=self.ui_settings.ui_font_color_1,
            relief="raised",
            font=(self.ui_settings.ui_font_type, self.ui_settings.ui_font_size),
        )

        label.grid(
            row=self.ui_inp_vars[dropdown_key].rel_pos,
            column=0,
            sticky="nsew",
        )
        max_len = max(len(item) for item in self.ui_inp_vars[dropdown_key].drop_options)
        max_len = 20
        combobox = ttk.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key].tk_var,
            values=self.ui_inp_vars[dropdown_key].drop_options or [],
            state="readonly" if self.ui_inp_vars[dropdown_key].state == "disabled" else "normal",
            font=(self.ui_settings.ui_font_type, self.ui_settings.ui_font_size),
            width=max_len,
        )
        combobox.grid(
            row=self.ui_inp_vars[dropdown_key].rel_pos,
            column=1,
            sticky="nsew",
        )
