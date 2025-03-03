import json
import shutil
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
import xlwings as xw
from PIL import Image, ImageTk

from rss_islandr.core.config_parser import XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable


class IOBtns(ABC):
    """
    Interface of input-output buttons.
    """

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]):
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars

    def access_vars(self):
        """Access all input and calculated UI-variables"""
        self.saved_scenario = {}
        self.xlsx_pos, self.xlsx_vals = [], []

        #: Access input variables
        for key in self.ui_inp_vars:
            try:
                position = self.ui_inp_vars[key].excel_cell
                value = self.ui_inp_vars[key].tk_var.get()
                self.xlsx_pos.append(position)
                self.xlsx_vals.append(value)
                self.saved_scenario[key] = value
            except Exception:
                pass

        #: Access calculated variables
        for key in self.ui_calc_vars:
            try:
                position = self.ui_calc_vars[key].excel_cell
                value = self.ui_calc_vars[key].tk_var.get()
                self.xlsx_pos.append(position)
                self.xlsx_vals.append(f"{value}")
                self.saved_scenario[key] = f"{value}"
            except Exception:
                pass

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

        shutil.copy(XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY)
        try:
            app = xw.App(visible=False)
            try:
                workbook = xw.Book(XLSX_TEMPLATE_FILE_COPY)
            except FileNotFoundError:
                workbook = xw.Book()

            sheet = workbook.sheets[0]
            for value, position in zip(self.xlsx_vals, self.xlsx_pos):
                if position is not None:
                    sheet.range(position).value = value

            workbook.save(XLSX_TEMPLATE_FILE_COPY)
            workbook.close()
            app.quit()
            shutil.copy(XLSX_TEMPLATE_FILE_COPY, file_path)
            messagebox.showinfo("Success", "Values written to Excel successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

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
                # print(ui_inp_var, scenario_data[ui_inp_var])
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
        self.image_path = r"C:\Users\George\Documents\makge\Python\islandr\rss_islandr\rss_islandr\static\transport.png"  # Change to your actual image path
        self.original_image = Image.open(self.image_path).convert("RGBA")

        # Button to Open/Close Popup
        self.popup_window = None  # Track if popup is open

    def __show_popup(self, frame: tb.Frame):
        """Creates a new popup window displaying the image."""
        self.popup_window = tk.Toplevel(frame)
        # self.popup_window.title("Image Popup")

        # Resize Image to Fit Popup Window
        resized_image = self.original_image.resize((1800, 908), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        label = tk.Label(self.popup_window, image=self.photo)
        label.pack(padx=10, pady=10)

        # # Close popup when clicked
        # self.popup_window.bind("<Button-1>", lambda e: self.on_btn_click())

    def on_btn_click(self, frame: tb.Frame):
        """Opens or closes the popup window with the image."""
        if self.popup_window and tk.Toplevel.winfo_exists(self.popup_window):
            self.popup_window.destroy()  # Close if already open
            self.popup_window = None
        else:
            self.__show_popup(frame)  # Open if closed

    def btn(self):
        pass
