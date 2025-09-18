# -*- coding: utf-8 -*-
import ttkbootstrap as tb

from rss_islandr.core.datatypes import FramePlacing, UIInpVariable, UISettings
from rss_islandr.core.logger_config import logger_decorator


@logger_decorator
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
        Parameters
        ----------
        ui_settings : UISettings
            This is a dataclass that holds the ui settings.
            It is always initialized using the dark theme option,
            but gets updated when the toggle button is pressed.
        ui_inp_vars : dict[str, UIInpVariable]
            Dictionary that maps the input variables aliases to UI input variables.
        frame_geometry_dict : dict[str, FramePlacing]
            Dictionary that maps the frame tags to their geometry as
            defined in the settings.json file.
        **kwargs:
        widgets_reconfigured : dict[TkWidgets, str]
            This dictionary maps the widget to the bootsyle (as a string)
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

    @logger_decorator
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

    @logger_decorator
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

    @logger_decorator
    def gt_new_frame_wo(self, parent_frame: tb.Frame, frame_tag: str) -> tb.Frame:
        """Create new frame without title (used in risk meters)"""
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.frame_limits(frame_tag)
        frame = tb.Frame(parent_frame, name=frame_tag.lower(), style="Custom.TFrame")
        frame.place(
            relx=rel_x,
            rely=rel_y,
            relwidth=rel_w,
            relheight=rel_h,
        )
        frame_distances(frame, n_rows, n_cols)

        return frame

    @logger_decorator
    def gt_entry_widget(self, frame: tb.Frame, entry_key: str, column_span: int = 1) -> None:
        """Create an entry widget"""
        label = tb.Label(frame, text=self.ui_inp_vars[entry_key].text_val)
        label.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=0, sticky="we")

        entry = tb.Entry(frame, textvariable=self.ui_inp_vars[entry_key].tk_var, justify="left")
        entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, columnspan=column_span, sticky="we")

    @logger_decorator
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

    @logger_decorator
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

    @logger_decorator
    def gt_meter_widget(self, frame: tb.Frame, meter_widget_text: str) -> tb.Meter:
        """Create a meter widget and place it in a frame"""
        meter_widget = tb.Meter(
            frame,
            amountused=0,
            amounttotal=100,
            metertype="full",
            subtext=meter_widget_text,
            textright="%",
            interactive=False,
            arcoffset=None,
            arcrange=None,
        )

        meter_widget.grid(row=0, column=0, sticky="ew")

        return meter_widget

    @logger_decorator
    def gt_date_entry_widget(self, frame: tb.Frame, date_key: str, column_span: int = 1) -> None:
        """
        Create a date entry widget doing the following:
            1. Trace change in the tb.StringVal.
            2. Bind it with FocusOut.
            3. Assign it to self.__widgets_reconfigured (change color if UI skin is altered).
        """
        label = tb.Label(frame, text=self.ui_inp_vars[date_key].text_val)
        label.grid(row=self.ui_inp_vars[date_key].rel_pos, column=0, sticky="we")
        date_var = self.ui_inp_vars[date_key].tk_var
        date_entry = tb.DateEntry(frame, bootstyle=self.ui_settings.ui_bg_color_1, dateformat="%Y-%m-%d")
        date_entry.grid(row=self.ui_inp_vars[date_key].rel_pos, column=1, columnspan=column_span, sticky="we")
        date_entry.entry.insert(0, date_var.get())

        date_var.trace_add("write", lambda *args: self.update_date_entry_trace(date_var, date_entry))
        date_entry.bind("<FocusOut>", lambda event: self.update_date_var_bind(event, date_entry, date_key))
        self.__widgets_reconfigured[date_entry] = "ui_bg_color_1"

    @logger_decorator
    def update_date_var_bind(self, event, date_entry: tb.DateEntry, date_key: str):
        """update_date_var_bind_bind"""
        date = date_entry.entry.get()
        self.ui_inp_vars[date_key].tk_var.set(date)  # type: ignore
        date_entry.entry.delete(0, "end")
        date_entry.entry.insert(0, date)

    @logger_decorator
    def update_date_entry_trace(self, date_var: tb.StringVar, date_entry: tb.DateEntry):
        """Update the DateEntry widget when the underlying tb.StringVar changes (eg. when importing scenario)."""
        new_date = date_var.get()
        date_entry.entry.delete(0, "end")
        date_entry.entry.insert(0, new_date)
