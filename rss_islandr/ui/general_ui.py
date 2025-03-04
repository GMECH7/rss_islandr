# -*- coding: utf-8 -*-
import ttkbootstrap as tb

from rss_islandr.core.datatypes import FramePlacing, UIInpVariable, UISettings


def frame_distances(frame: tb.Frame, n_rows: int, n_cols: int) -> None:
    """Configure frame in a grid."""
    for i in range(n_rows):
        frame.grid_rowconfigure(i, weight=1)
    for i in range(n_cols):
        frame.grid_columnconfigure(i, weight=1)


class GeneralUITemplate:
    """General widget templates."""

    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        frame_geometry_dict: dict[str, FramePlacing],
        **kwargs,
    ):
        """
        _summary_

        Parameters
        ----------
        ui_settings : UISettings
            _description_
        ui_inp_vars : dict[str, UIInpVariable]
            _description_
        frame_geometry_dict : dict[str, FramePlacing]
            _description_
        **kwargs:
        widgets_reconfigured : dict[tb.Frame, str]
            This dictionary holds the pair of frame and the bootsyle
            used in their rendering. All widgets that have a bootsyle
            which is not defined in the CustomThemes have to be included
            here in order to be restyled when the theme changes.
        """

        self.ui_inp_vars = ui_inp_vars
        self.ui_settings = ui_settings
        self.frame_geometry_dict = frame_geometry_dict
        self.__widgets_reconfigured = kwargs.get("widgets_reconfigured", {})

    def __str__(self):
        return str(__class__.__name__)

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

        return rel_x, rel_y, rel_w, rel_h, n_rows, n_cols

    def __add_title(
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
        frame_distances(title_frame, 0, 1)
        title_label = tb.Label(title_frame, text=frame_title, anchor="center", justify="center", style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky="nsew")

    def gt_new_frame(self, parent_frame: tb.Frame, frame_tag: str, frame_title: str) -> tb.Frame:
        """Create new frame with title (used in forms)"""
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        self.__add_title(parent_frame, frame_title, rel_x, rel_y, rel_w, rel_h)
        title_offset = 0.0 if frame_title == "" else self.ui_settings.ui_title_offset

        frame = tb.Frame(parent_frame)
        frame.place(
            relx=rel_x,
            rely=rel_y + title_offset,
            relwidth=rel_w,
            relheight=rel_h - title_offset,
        )
        frame_distances(frame, n_rows, n_cols)

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
        frame_distances(frame, n_rows, n_cols)

        return frame

    def gt_entry_widget(self, frame: tb.Frame, entry_key: str, column_span: int = 1) -> None:
        """Create an entry widget"""
        label = tb.Label(frame, text=self.ui_inp_vars[entry_key].text_val)
        label.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=0, sticky="we")

        entry = tb.Entry(frame, textvariable=self.ui_inp_vars[entry_key].tk_var, justify="left")
        entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, columnspan=column_span, sticky="we")

    def gt_combobox_widget(self, frame: tb.Frame, dropdown_key: str, column_span: int = 1) -> None:
        """Create a combobox widget (dropdown list)"""
        label = tb.Label(frame, text=self.ui_inp_vars[dropdown_key].text_val)
        label.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=0, sticky="we")

        combobox = tb.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key].tk_var,
            values=self.ui_inp_vars[dropdown_key].drop_options or [],
        )

        combobox.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=1, columnspan=column_span, sticky="we")

    def gt_nested_combobox_widget(self, frame: tb.Frame, dropdown_key: str, column_span: int = 1) -> None:
        """Create a combobox widget (dropdown list)."""
        label = tb.Label(frame, text=self.ui_inp_vars[dropdown_key].text_val)
        label.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=0, sticky="we")

        combobox = tb.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key].tk_var,
            values=self.ui_inp_vars[dropdown_key].drop_options or [],
        )

        combobox.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=1, columnspan=column_span, sticky="we")
        dropdown_key_2 = dropdown_key[:-2] + f"0{int(dropdown_key[-2:]) + 1}"

        combobox = tb.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key_2].tk_var,
            values=self.ui_inp_vars[dropdown_key_2].drop_options or [],
        )

        combobox.grid(row=self.ui_inp_vars[dropdown_key].rel_pos, column=2, columnspan=column_span, sticky="we")

    def gt_meter_widget(self, frame: tb.Frame, frame_tag: str) -> tb.Meter:
        """Create a meter widget and place it in a frame"""
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        meter_widget = tb.Meter(
            frame,
            amountused=0,
            metertype="full",
            subtext="Risk Level",
            interactive=False,
        )

        frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)
        frame_distances(frame, n_rows, n_cols)
        meter_widget.grid(row=0, column=0, sticky="nsew")

        return meter_widget

    def gt_date_entry_widget(self, frame: tb.Frame, date_key: str, column_span: int = 1) -> None:
        """
        Create a date entry widget doing the following:
            1. Bind it with FocusOut.
            2. Assign it to self.__widgets_reconfigured (change color if UI skin is altered).
        """
        label = tb.Label(frame, text=self.ui_inp_vars[date_key].text_val)
        label.grid(row=self.ui_inp_vars[date_key].rel_pos, column=0, sticky="we")
        date_entry = tb.DateEntry(frame, bootstyle=self.ui_settings.ui_bg_color_1, dateformat="%Y-%m-%d")
        date_entry.grid(row=self.ui_inp_vars[date_key].rel_pos, column=1, columnspan=column_span, sticky="we")
        date_entry.bind("<FocusOut>", lambda event: self.__update_date_var(event, date_entry, date_key))
        self.__widgets_reconfigured[date_entry] = "ui_bg_color_1"

    def __update_date_var(self, event, date_entry: tb.DateEntry, date_key: str):
        """ """
        date = date_entry.entry.get()
        self.ui_inp_vars[date_key].tk_var.set(date)  # type: ignore
