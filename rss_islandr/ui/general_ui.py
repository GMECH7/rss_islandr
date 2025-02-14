# -*- coding: utf-8 -*-
import distutils.util as Bool
import os
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageTk

from rss_islandr.core.config_parser import (
    font_type,
    ui_bg_color_1,
    ui_bg_color_2,
    ui_font_color_1,
    ui_font_color_2,
)
from rss_islandr.core.datatypes import UIVariable


class GeneralUITemplate:

    def __init__(
        self,
        ui_inp_vars: dict[str, UIVariable],
        root: tk.Toplevel,
        frame_info: dict[str, list[float]],
        canvas_height,
        canvas_width,
    ):
        """ """
        self.ui_inp_vars = ui_inp_vars
        self.root = root
        self.frame_info = frame_info
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        # Maps drop parameter name (eg. 'drop_0_01') to drop object
        # This way the object can be used in a callback when its value is traced by another parameter
        self.param_to_obj_dict = {}
        # Update of this dictionary is made on the class that inherits
        self.ui_inputs_merged = {}
        self.__define_colors_fonts()
        self.__define_colors_bg()
        self.message_variable = tk.StringVar()
        self.__ere_frame_tag = "ere_frame"
        self.__ere_frame_title = "Execute"
        self.title_offset = 0.030

    def __str__(self):
        """ """
        return str(__class__.__name__)

    def __define_colors_fonts(self):
        """
        Used in __init__.
        """
        self.title_font = "calibri"
        self.title_font_size = 12
        self.font = font_type
        self.fontsize = 12
        self.title_font_color = ui_font_color_1
        self.entry_font_color = ui_font_color_2
        self.button_font_color = ui_font_color_1
        self.label_font_color = ui_font_color_1  # "#%02x%02x%02x" % (153, 230, 106)
        self.message_font_color_None_exception = "#%02x%02x%02x" % (153, 230, 106)
        self.message_font_color_exception = ui_font_color_1
        self.message_font_color = self.message_font_color_None_exception
        self.dropdown_font_color = self.entry_font_color

    def __define_colors_bg(self):
        """
        Used in __init__.\n
        """
        self.background_color = ui_bg_color_1
        self.button_color = ui_bg_color_1
        self.title_color = ui_bg_color_2
        self.frame_color = ui_bg_color_2
        self.entry_color = ui_bg_color_2
        self.label_color = ui_bg_color_2
        self.dropdown_color = self.entry_color

    def __close_window(self, current_root) -> None:
        """
        Close window.
        """
        current_root.destroy()

    def __restore_defaults(self, last_settings_file) -> None:
        """
        Restore defaults.
        """
        if os.path.exists(last_settings_file):
            os.remove(last_settings_file)
            self.general_update_message(
                "Inputs have been restored to its default values. Please close and reopen the window."
            )
        else:
            self.general_update_message("No action taken. These are the default inputs.")

    def __exception_messages(self) -> dict[int, str]:
        """
        Exception messages.\n
        """
        exception_messages = {
            1: "Check one of the input that should be string",
            2: "Check one of the input that should be boolean",
            3: "Check one of the input that should be list",
            4: "Check one of the input that should be float",
            5: "Check one of the input that should be integer",
        }

        return exception_messages

    def __retrieve_strings(self, *args) -> tuple:
        """
        Retrieve a dynamic number of string variables.
        """
        strings = ()
        for string_var in args:
            strings += (f"{string_var.get()}",)

        return strings

    def __retrieve_booleans(self, *args) -> tuple:
        """
        Retrieve a dynamic number of boolean variables.
        """
        booleans = ()
        for boolean_var in args:
            booleans += (Bool.strtobool(boolean_var.get()),)

        return booleans

    def __retrieve_lists(self, *args) -> tuple:
        """
        Retrieve a dynamic number of lists.
        """
        lists = ()
        for list_var in args:
            list_ = list_var.get()
            list_ = list_.split(",")
            list_ = [item.strip() for item in list_]
            lists += (list_,)

        return lists

    def __retrieve_floats(self, *args) -> tuple:
        """
        Retrieve a dynamic number of float variables.
        """
        floats = ()
        for float_var in args:
            floats += (float(float_var.get()),)
        return floats

    def __retrieve_integers(self, *args) -> tuple:
        """
        Retrieve a dynamic number of integer variables.
        """
        ints = ()
        for int_var in args:
            ints += (int(int_var.get()),)

        return ints

    def __frame_distances(self, frame: tk.Frame, n_rows: int, n_cols: int) -> None:
        """ """
        for i in range(n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(n_cols):
            frame.grid_columnconfigure(i, weight=1)

        return None

    def __template_title(self, frame_title, rel_x, rel_y, rel_w, rel_h) -> None:
        """ """
        title_frame = tk.Frame(self.root, bg=self.frame_color)
        title_frame.place(relx=rel_x, rely=rel_y, relwidth=rel_w, relheight=rel_h)
        self.__frame_distances(title_frame, 0, 1)
        title_label = tk.Label(
            title_frame,
            text=frame_title,
            bg=self.title_color,
            fg=self.title_font_color,
            relief="raised",
            justify="center",
        )
        title_label.grid(row=0, column=0, sticky="nsew")
        title_label.config(font=(self.title_font, self.title_font_size))

        return None

    def __manage_new_columns(self, cell_incr_pos, new_col_criterion) -> tuple:
        """
        Auxiliary method used for determining the index of the row and column\n
        for the different type of entries.\n
        Keyword arguments:\n
            cell_incr_pos : int -> Incremental position of the parameter handled.\n
            new_col_criterion : int -> Number of positions after which a new column\n
            will be created.\n
        """
        col1, col2 = 0, 1
        if cell_incr_pos >= new_col_criterion:
            cell_incr_pos -= new_col_criterion
            col1 += 2
            col2 += 2

        return cell_incr_pos, col1, col2

    def __frames_limits(self, frame_tag) -> tuple:
        """
        Auxiliary method used for specifying the relative frame limits of each frame\n
        (the first 4 numbers) as well as the default number of rows and columns expected\n
        in each frame.\n
        Keyword arguments:\n
            frame_tag : Frame name.\n
        """
        rel_x = self.frame_info[frame_tag][0]
        rel_y = self.frame_info[frame_tag][1]
        rel_w = self.frame_info[frame_tag][2]
        rel_h = self.frame_info[frame_tag][3]
        n_rows = self.frame_info[frame_tag][4]
        n_cols = self.frame_info[frame_tag][5]

        return rel_x, rel_y, rel_w, rel_h, n_rows, n_cols

    def __get_current_time(self) -> str:
        """
        Method used for getting the current time.\n
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        return current_time

    def __calculate_hrs_mins_secs(self, end_time: float, start_time: float) -> str:
        """ """
        timedelta_seconds = end_time - start_time
        hours = int(timedelta_seconds // 3600)
        minutes = int((timedelta_seconds % 3600) // 60)
        seconds = timedelta_seconds % 60
        if hours == 0 and minutes == 0:
            hms = f"{round(seconds,4)}s"
        elif hours == 0 and minutes != 0:
            hms = f"{minutes}min::{round(seconds,2)}s"
        else:
            hms = f"{hours}h::{minutes}min::{round(seconds,2)}s"
        return hms

    def __ere_handle_orientation(self, orientation) -> tuple:
        """ """
        if orientation == "horizontal":
            rows_list = [0, 0, 0]
            cols_list = [0, 1, 2]
        else:
            rows_list = [0, 1, 2]
            cols_list = [0, 0, 0]

        return rows_list, cols_list

    def __import_icons_ere_buttons(self, package_dir, frame_tag) -> None:
        """
        Method used for importing the icons for the execute-restore-exit buttons.\n
        Note!!
        When using PIL.ImageTk.PhotoImage in a Tkinter application, it's important\n
        to ensure that the image object remains referenced as long as the widget\n
        using it exists. If the image object gets garbage collected, it can lead\n
        to the button (or any other widget) becoming non-functional.
        """
        _, _, rel_w, rel_h, n_rows, n_cols = self.__frames_limits(frame_tag)
        icons_to_import = ["player.ico", "restore.ico", "exit.ico"]
        self.images_icons = []
        for ico in icons_to_import:
            ico_imported = Image.open(f"{package_dir}\\static\\{ico}")
            width, height = ico_imported.size
            aspect_ratio = width / height
            pixels_h = int(0.5 * rel_h * self.canvas_height / n_rows)
            pixels_w = int(0.5 * rel_w * self.canvas_width / n_cols)

            if pixels_h <= pixels_w:
                icon_height = pixels_h
                icon_width = int(aspect_ratio * icon_height)
            else:
                icon_width = pixels_w
                icon_height = int(icon_width * 1.0 / aspect_ratio)
            ico_imported = ico_imported.resize((icon_width, icon_height), Image.Resampling.LANCZOS)
            self.images_icons.append(ImageTk.PhotoImage(ico_imported))

    def __ere_execute_button(
        self,
        ere_buttons_frame,
        rows_list,
        cols_list,
        retrieve_main_func_args,
        main_func_to_exec,
        class_or_func,
    ) -> None:
        """ """
        execute_button = tk.Button(
            ere_buttons_frame,
            image=self.images_icons[0],  # Set the image
            text="Execute",
            compound="left",  # Display image and text side by side
            bg=self.button_color,
            fg=self.button_font_color,
            command=lambda: self.__general_execute(
                retrieve_main_func_args, main_func_to_exec, class_or_func
            ),
        )
        execute_button.grid(row=rows_list[0], column=cols_list[0], sticky="nsew")
        execute_button.config(font=(self.font, self.fontsize))

    def __ere_default_button(
        self, ere_buttons_frame, rows_list, cols_list, last_settings_file
    ) -> None:
        """ """
        default_button = tk.Button(
            ere_buttons_frame,
            image=self.images_icons[1],  # Set the image
            text="Restore",
            compound="left",  # Display image and text side by side
            bg=self.button_color,
            fg=self.button_font_color,
            command=lambda: self.__restore_defaults(last_settings_file),
        )

        default_button.grid(row=rows_list[1], column=cols_list[1], sticky="nsew")
        default_button.config(font=(self.font, self.fontsize))

    def __ere_exit_button(self, ere_buttons_frame, rows_list, cols_list, root) -> None:
        """ """
        exit_button = tk.Button(
            ere_buttons_frame,
            image=self.images_icons[2],  # Set the image
            text="EXIT",
            compound="left",  # Display image and text side by side
            bg=self.button_color,
            fg=self.button_font_color,
            command=lambda: self.__close_window(root),
        )

        exit_button.grid(row=rows_list[2], column=cols_list[2], sticky="nsew")
        exit_button.config(font=(self.font, self.fontsize))
        return None

    def __general_execute(self, retrieve_main_func_args, main_func_to_exec, class_or_func):
        """
        Execute main script.
        """
        args = retrieve_main_func_args()
        try:
            start_time = time.time()
            print_ui_message = "Program Execution started !!\n"
            self.general_update_message(print_ui_message)
            if class_or_func == "func":
                main_func_to_exec(*args)
            else:
                exec_obj = main_func_to_exec(args)
                exec_obj()
            end_time = time.time()
            hms = self.__calculate_hrs_mins_secs(end_time, start_time)

            print_ui_message += f"\nSuccessful Execution. {self.__get_current_time()}"
            print_ui_message += f"\nTime elapsed :  {hms}"
            self.general_update_message(print_ui_message)
        except Exception as ex:
            print_ui_message = f"Execution exception : {ex}"
            print_ui_message = "\n".join(wrap(print_ui_message, 80))
            self.message_font_color = self.message_font_color_exception
            self.general_update_message(print_ui_message)
            sys.exit()

        return None

    def __access_ui_inputs_merged(self, param, case) -> tuple:
        """ """
        cell_incr_pos = self.ui_inputs_merged[param][1]
        cell_value_tk = self.ui_inputs_merged[param][2]
        cell_options = self.ui_inputs_merged[param][3]
        cell_text = self.ui_inputs_merged[param][4]
        cell_state = self.ui_inputs_merged[param][5]
        if case == "dropdown":
            cell_state_tk = tk.DISABLED if cell_state == "disabled" else tk.ACTIVE
        else:
            cell_state_tk = tk.DISABLED if cell_state == "disabled" else tk.NORMAL

        return cell_incr_pos, cell_value_tk, cell_options, cell_text, cell_state_tk

    def general_template_frames(self, frame_tag: str, frame_title: str) -> tk.Frame:
        """ """
        rel_x, rel_y, rel_w, rel_h, n_rows, n_cols = self.__frames_limits(frame_tag)
        self.__template_title(frame_title, rel_x, rel_y, rel_w, rel_h)
        title_offset = 0.0 if frame_title == "" else self.title_offset

        frame = tk.Frame(self.root, bg=self.frame_color)
        frame.place(
            relx=rel_x,
            rely=rel_y + title_offset,
            relwidth=rel_w,
            relheight=rel_h - title_offset,
        )
        self.__frame_distances(frame, n_rows, n_cols)

        return frame

    # def general_template_entries(self, frame, param_entry, new_col_criterion) -> None:
    #     """
    #     The template of the entries.\n
    #     Keyword arguments:\n
    #         frame : frame instance (different from frame_tag).\n
    #         param_entry : The Entry parameter name (dictionary key).\n
    #         new_col_criterion : int -> Number of positions after which a new column\n
    #                             will be created.\n
    #     """
    #     cell_incr_pos, cell_value_tk, _, cell_text, cell_state_tk = self.__access_ui_inputs_merged(
    #         param_entry, "entry"
    #     )
    #     row_, col1, col2 = self.__manage_new_columns(cell_incr_pos, new_col_criterion)

    #     label = tk.Label(
    #         frame,
    #         text=cell_text,
    #         bg=self.label_color,
    #         fg=self.label_font_color,
    #         relief="raised",
    #     )

    #     label.grid(row=row_, column=col1, sticky="nsew")
    #     label.config(font=(self.font, self.fontsize))
    #     entry = tk.Entry(
    #         frame,
    #         textvariable=cell_value_tk,
    #         bg=self.entry_color,
    #         fg=self.entry_font_color,
    #         relief="raised",
    #         justify="center",
    #         state=cell_state_tk,
    #     )

    #     entry.grid(row=row_, column=col2, sticky="nsew")
    #     entry.config(font=(self.font, self.fontsize))

    #     dict_ = {param_entry: entry}
    #     self.param_to_obj_dict.update(dict_)

    #     return None

    def general_template_entries(self, frame: tk.Frame, entry_key: str) -> None:

        label = tk.Label(
            frame,
            text=self.ui_inp_vars[entry_key].text_val,
            bg=self.label_color,
            fg=self.label_font_color,
            relief="raised",
        )

        label.grid(
            row=self.ui_inp_vars[entry_key].rel_pos,
            column=0,
            sticky="nsew",
        )

        label.config(font=(self.font, self.fontsize))

        entry = tk.Entry(
            frame,
            textvariable=self.ui_inp_vars[entry_key].tk_var,
            bg=self.entry_color,
            fg=self.entry_font_color,
            relief="raised",
            justify="center",
        )

        entry.grid(row=self.ui_inp_vars[entry_key].rel_pos, column=1, sticky="nsew")
        entry.config(font=(self.font, self.fontsize))

        dict_ = {entry_key: entry}
        self.param_to_obj_dict.update(dict_)

        return None

    def general_template_dropdown(self, frame: tk.Frame, dropdown_key: str) -> None:

        label = tk.Label(
            frame,
            text=self.ui_inp_vars[dropdown_key].text_val,
            bg=self.label_color,
            fg=self.label_font_color,
            relief="raised",
            font=(self.font, self.fontsize),
        )

        label.grid(
            row=self.ui_inp_vars[dropdown_key].rel_pos,
            column=0,
            sticky="nsew",
        )

        combobox = ttk.Combobox(
            frame,
            textvariable=self.ui_inp_vars[dropdown_key].tk_var,
            values=self.ui_inp_vars[dropdown_key].drop_options or [],
            state="readonly" if self.ui_inp_vars[dropdown_key].state == "disabled" else "normal",
            font=(self.font, self.fontsize),
        )
        combobox.grid(
            row=self.ui_inp_vars[dropdown_key].rel_pos,
            column=1,
            sticky="nsew",
        )

        self.param_to_obj_dict[dropdown_key] = combobox

    # def general_template_dropdown(self, frame: tk.Frame, param_dropdown, new_col_criterion) -> None:
    #     """
    #     The template of the dropdown list using Combobox.

    #     Keyword arguments:
    #         frame : frame instance (see: self.general_template_frames()).
    #         param_dropdown : The Entry parameter name (dictionary key).
    #         new_col_criterion : int -> Number of positions after which a new column
    #                             will be created.
    #     """
    #     cell_incr_pos, cell_value_tk, cell_options, cell_text, cell_state_tk = (
    #         self.__access_ui_inputs_merged(param_dropdown, "dropdown")
    #     )

    #     row_, col1, col2 = self.__manage_new_columns(cell_incr_pos, new_col_criterion)

    #     # Create label
    #     label = tk.Label(
    #         frame,
    #         text=cell_text,
    #         bg=self.label_color,
    #         fg=self.label_font_color,
    #         relief="raised",
    #         font=(self.font, self.fontsize),
    #     )
    #     label.grid(row=row_, column=col1, sticky="nsew")

    #     # Create Combobox
    #     combobox = ttk.Combobox(
    #         frame,
    #         textvariable=cell_value_tk,
    #         values=cell_options,
    #         state="readonly" if cell_state_tk == "disabled" else "normal",
    #         font=(self.font, self.fontsize),
    #     )
    #     combobox.grid(row=row_, column=col2, sticky="nsew")

    #     # Store in dictionary
    #     self.param_to_obj_dict[param_dropdown] = combobox

    def general_retriever(self, case, *args) -> tuple:
        """
        Keyword arguments:\n
            case:\n
            1: string, 2: booleans, 3:list, 4:floats, 5:integers.\n
        """
        try:
            if case == 1:
                return_tuple = self.__retrieve_strings(*args)
            elif case == 2:
                return_tuple = self.__retrieve_booleans(*args)
            elif case == 3:
                return_tuple = self.__retrieve_lists(*args)
            elif case == 4:
                return_tuple = self.__retrieve_floats(*args)
            elif case == 5:
                return_tuple = self.__retrieve_integers(*args)
            if len(return_tuple) == 1:  # if len==1 -> (<var>, ) otherwise , is autodeleted
                return return_tuple[0]
            else:
                return return_tuple
        except Exception as ex:
            print_ui_message = self.__exception_messages()[case]
            self.general_update_message(f"{print_ui_message}\n{ex}")
            raise Exception

    def general_message_frame(self) -> tk.Label:
        """
        Message frame.
        """
        frame_tag = "message_frame"
        frame_title = ""
        bottom_frame = self.general_template_frames(frame_tag, frame_title)

        msg = tk.Label(
            bottom_frame,
            textvariable=self.message_variable,
            bg=self.label_color,
            fg=self.message_font_color,
        )
        msg.place(relx=0, rely=0, relwidth=1, relheight=1)

        return msg

    def general_update_message(self, print_ui_message) -> None:
        """
        Update message in message frame.
        """
        self.general_message_frame()
        self.message_variable.set(print_ui_message)
        self.root.update_idletasks()
        self.root.update()
        self.message_font_color = self.message_font_color_None_exception

        return None

    def general_ere_buttons(
        self,
        package_dir: Path,
        root: tk.Toplevel,
        last_settings_file: Path,
        orientation: str,
        retrieve_main_func_args: Callable[..., dict[str, tuple]],
        main_func_to_exec: Callable,
        class_or_func: str,
    ) -> None:
        """
        Execute/Restore defaults/Exit button.\n
        Keyword arguments:\n
            root : tk.Tk object.\n
            last_settings_file : Path to last user settings.\n
            orientation : Orientation of buttons 'vertical' or 'horizontal'.\n
            retrieve_main_func_args : Function of inheriting class that retrieves\n
                arguments to be used in main_func_to_exec.\n
            main_func_to_exec : Function (or class) to be executed. Imported in inherited class\n
                definition .py and defined in the main folder of this project.\n
            class_or_func : 'func' and 'class' option. If 'class' then a __call__\n
                method has been implemented instead of the traditional functional call.\n
        """
        rows_list, cols_list = self.__ere_handle_orientation(orientation)
        self.__import_icons_ere_buttons(package_dir, self.__ere_frame_tag)
        ere_buttons_frame = self.general_template_frames(
            self.__ere_frame_tag, self.__ere_frame_title
        )

        self.__ere_execute_button(
            ere_buttons_frame,
            rows_list,
            cols_list,
            retrieve_main_func_args,
            main_func_to_exec,
            class_or_func,
        )

        self.__ere_default_button(ere_buttons_frame, rows_list, cols_list, last_settings_file)

        self.__ere_exit_button(ere_buttons_frame, rows_list, cols_list, root)

        return None
