# -*- coding: utf-8 -*-
import ttkbootstrap as tb

from rss_islandr.core.datatypes import FramePlacing, UIInpVariable, UISettings


class GeneralUITemplate:
    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        frame_geometry_dict: dict[str, FramePlacing],
    ):
        self.ui_inp_vars = ui_inp_vars
        self.ui_settings = ui_settings
        self.frame_geometry_dict = frame_geometry_dict

    def __str__(self):
        return str(__class__.__name__)

    def frame_distances(self, frame: tb.Frame, n_rows: int, n_cols: int) -> None:
        for i in range(n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(n_cols):
            frame.grid_columnconfigure(i, weight=1)

    def frame_limits(self, frame_tag: str) -> tuple:
        rel_x = self.frame_geometry_dict[frame_tag].x_l
        x_r = self.frame_geometry_dict[frame_tag].x_r

        rel_y = self.frame_geometry_dict[frame_tag].y_u
        y_d = self.frame_geometry_dict[frame_tag].y_d

        rel_w = x_r - rel_x
        rel_h = y_d - rel_y

        n_rows = self.frame_geometry_dict[frame_tag].n_row
        n_cols = self.frame_geometry_dict[frame_tag].n_col

        return rel_x, rel_y, rel_w, rel_h, n_rows, n_cols

    def template_title(
        self,
        parent_frame: tb.Frame,
        frame_title: str,
        rel_x: float,
        rel_y: float,
        rel_w: float,
        rel_h: float,
    ) -> None:
        title_frame = tb.Frame(parent_frame)
        title_frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)
        self.frame_distances(title_frame, 0, 1)
        title_label = tb.Label(title_frame, text=frame_title, anchor="center", justify="center", style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky="nsew")

    # def gt_new_frame(self, parent_frame: tb.Frame, frame_tag: str, frame_title: str) -> tb.Frame:
    #     """Create new frame with title (used in forms)"""
    #     rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
    #     self.template_title(parent_frame, frame_title, rel_x, rel_y, rel_w, rel_h)
    #     title_offset = 0.0 if frame_title == "" else self.ui_settings.ui_title_offset

    #     frame = tb.Frame(parent_frame, style="Custom.TFrame")
    #     frame.place(
    #         relx=rel_x,
    #         rely=rel_y + title_offset,
    #         relwidth=rel_w,
    #         relheight=rel_h - title_offset,
    #     )
    #     self.frame_distances(frame, n_rows, n_cols)

    #     return frame

    def gt_new_frame(self, parent_frame: tb.Frame, frame_tag: str, frame_title: str) -> tb.Frame:
        """Create new frame with title (used in forms)"""
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        self.template_title(parent_frame, frame_title, rel_x, rel_y, rel_w, rel_h)
        title_offset = 0.0 if frame_title == "" else self.ui_settings.ui_title_offset

        frame = tb.Frame(parent_frame)
        frame.place(
            relx=rel_x,
            rely=rel_y + title_offset,
            relwidth=rel_w,
            relheight=rel_h - title_offset,
        )
        self.frame_distances(frame, n_rows, n_cols)

        return frame

    def gt_new_frame_wo(self, parent_frame: tb.Frame, frame_tag: str) -> tb.Frame:
        """Create new frame without title (used in risk meters)"""
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        frame = tb.Frame(parent_frame, style="Custom.TFrame")
        frame.place(
            relx=rel_x,
            rely=rel_y,
            relwidth=rel_w,
            relheight=rel_h,
        )
        self.frame_distances(frame, n_rows, n_cols)

        return frame

    # def gt_entry_widget(self, frame: tb.Frame, entry_key: str) -> None:
    #     label = tb.Label(frame, text=self.ui_inp_vars[entry_key].text_val, style="General.TLabel")
    #     label.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=0, sticky="nsew")

    #     entry = tb.Entry(
    #         frame,
    #         textvariable=self.ui_inp_vars[entry_key].tk_var,
    #         justify="left",
    #         style="EntryWidget.TLabel",
    #     )
    #     entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, sticky="nsew")

    def gt_entry_widget(self, frame: tb.Frame, entry_key: str) -> None:
        label = tb.Label(frame, text=self.ui_inp_vars[entry_key].text_val)
        label.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=0, sticky="we")

        entry = tb.Entry(frame, textvariable=self.ui_inp_vars[entry_key].tk_var, justify="left")
        entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, sticky="we")

    # def gt_combobox_widget(self, frame: tb.Frame, dropdown_key: str) -> None:
    #     label = tb.Label(
    #         frame,
    #         text=self.ui_inp_vars[dropdown_key].text_val,
    #         style="General.TLabel",
    #     )
    #     label.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=0, sticky="nsew")

    #     combobox = tb.Combobox(
    #         frame,
    #         style="Custom.TCombobox",  # Apply the custom style
    #         textvariable=self.ui_inp_vars[dropdown_key].tk_var,
    #         values=self.ui_inp_vars[dropdown_key].drop_options or [],
    #     )

    #     combobox.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=1, sticky="nsew")

    def gt_combobox_widget(self, frame: tb.Frame, dropdown_key: str) -> None:
        label = tb.Label(frame, text=self.ui_inp_vars[dropdown_key].text_val)
        label.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=0, sticky="we")

        combobox = tb.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key].tk_var,
            values=self.ui_inp_vars[dropdown_key].drop_options or [],
        )

        combobox.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=1, sticky="we")

    def gt_meter_widget(self, frame: tb.Frame, frame_tag: str) -> tb.Meter:
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        meter_widget = tb.Meter(
            frame,
            amountused=0,  # Initial value (e.g., 0%)
            metertype="full",  # Type of meter: "full", "semi", or "arc"
            subtext="Risk Level",  # Text below the meter
            interactive=False,  # Disable user interaction
        )
        frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)

        self.frame_distances(frame, n_rows, n_cols)
        meter_widget.grid(row=0, column=0, sticky="nsew")

        return meter_widget
