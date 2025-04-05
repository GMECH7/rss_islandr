import json
import logging
import shutil
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
import xlwings as xw
from PIL import Image, ImageTk

from rss_islandr.core.config_parser import STATIC_DIR, XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable

logging.basicConfig(level=logging.INFO)


class IOBtns(ABC):
    """
    Interface of input-output buttons.
    """

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.saved_scenario = {}
        self.xlsx_sheet_pos_vals = {"on-on": [], "on-off": [], "off-on": []}

    def __access_vars_loop(self, key: str, vars_dict):
        """ """
        try:
            position = vars_dict[key].excel_cell
            value = vars_dict[key].tk_var.get()
            if "on-on" in key:
                self.xlsx_sheet_pos_vals["on-on"].append((position, value))
            elif "on-off" in key:
                self.xlsx_sheet_pos_vals["on-off"].append((position, value))
            elif "off-on" in key:
                self.xlsx_sheet_pos_vals["off-on"].append((position, value))
            else:
                self.xlsx_sheet_pos_vals["on-on"].append((position, value))
                self.xlsx_sheet_pos_vals["on-off"].append((position, value))
                self.xlsx_sheet_pos_vals["off-on"].append((position, value))
            self.saved_scenario[key] = value
        except Exception as ex:
            logging.debug(f"Error accessing {key}: {ex}")

    def access_vars(self):
        """Access all input and calculated UI-variables"""
        #: Access input variables
        for key in self.ui_inp_vars:
            self.__access_vars_loop(key, self.ui_inp_vars)
        #: Access calculated variables
        for key in self.ui_calc_vars:
            self.__access_vars_loop(key, self.ui_calc_vars)

    @abstractmethod
    def on_btn_click(self, *args):
        """ """
        pass

    @abstractmethod
    def btn(self, *args):
        """ """
        pass


class ExportExcelReportBtn(IOBtns):
    """Implementation of button for exporting to excel file"""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        super().__init__(ui_inp_vars, ui_calc_vars)

    def on_btn_click(self):
        """ """
        self.access_vars()

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("XLSX files", "*.xlsx"), ("All files", "*.*")],
            title="Save Scenario As",
        )
        if not file_path:  # User canceled the dialog
            return

        shutil.copy(XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY)
        try:
            app = xw.App(visible=False)
            try:
                workbook = xw.Book(XLSX_TEMPLATE_FILE_COPY)
            except FileNotFoundError:
                workbook = xw.Book()

            for sheet_name_key in self.xlsx_sheet_pos_vals:
                if sheet_name_key == "on-on":
                    sheet = workbook.sheets[0]
                elif sheet_name_key == "on-off":
                    sheet = workbook.sheets[1]
                elif sheet_name_key == "off-on":
                    sheet = workbook.sheets[2]

                for position, value in self.xlsx_sheet_pos_vals[sheet_name_key]:
                    logging.debug(f"Writing {value} to {sheet} {position}")
                    if position is not None:
                        sheet.range(position).value = value

            workbook.save(XLSX_TEMPLATE_FILE_COPY)
            workbook.close()
            app.quit()
            shutil.copy(XLSX_TEMPLATE_FILE_COPY, file_path)
            messagebox.showinfo("Success", "Values written to Excel successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An erroree occurred: {e}")

    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Write to Excel", command=self.on_btn_click)

        return btn


class ExportScenarioBtn(IOBtns):
    """Implementation of button for exporting a scenario to a json file."""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        super().__init__(ui_inp_vars, ui_calc_vars)

    def on_btn_click(self):
        """ """
        self.access_vars()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Scenario As",
        )

        if not file_path:  # User canceled the dialog
            return
        try:
            with open(file_path, "w") as scenario_file:
                json.dump(self.saved_scenario, scenario_file, indent=4)
                messagebox.showinfo("Success", "Scenario values exported!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Save scenario", command=self.on_btn_click)
        return btn


class ImportScenarioBtn(IOBtns):
    """Implementation of button for importing a scenario from a json file."""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        super().__init__(ui_inp_vars, ui_calc_vars)

    def on_btn_click(self):
        """ """
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open Scenario",
        )
        if not file_path:  # User canceled the dialog
            return
        try:
            with open(file_path, "r") as file_inp:
                scenario_data = json.load(file_inp)
            for ui_inp_var in self.ui_inp_vars:
                self.ui_inp_vars[ui_inp_var].tk_var.set(scenario_data[ui_inp_var])
            messagebox.showinfo("Success", "Scenario values imported!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Read scenario", command=self.on_btn_click)
        return btn


class PopupImage(IOBtns):
    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        super().__init__(ui_inp_vars, ui_calc_vars)
        self.image_path = STATIC_DIR / "csm.png"  # Change to your actual image path
        self.original_image = Image.open(self.image_path).convert("RGBA")

        # Button to Open/Close Popup
        self.popup_window = None  # Track if popup is open

    def __show_popup(self, frame: tb.Frame):
        """Creates a new popup window displaying the image."""
        self.popup_window = tk.Toplevel(frame)

        # Resize Image to Fit Popup Window
        resized_image = self.original_image.resize((1800, 908), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        label = tk.Label(self.popup_window, image=self.photo)
        label.pack(padx=10, pady=10)

    def on_btn_click(self, frame: tb.Frame):
        """Opens or closes the popup window with the image."""
        if self.popup_window and tk.Toplevel.winfo_exists(self.popup_window):
            self.popup_window.destroy()  # Close if already open
            self.popup_window = None
        else:
            self.__show_popup(frame)  # Open if closed

    def btn(self):
        pass
