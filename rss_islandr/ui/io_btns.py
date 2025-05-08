import json
import logging
import os
import shutil
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import filedialog, messagebox

import ttkbootstrap as tb
import xlwings as xw
from PIL import Image, ImageTk

from rss_islandr.core.config_parser import (
    SAVED_MAPS_IMAGES_DIR,
    STATIC_DIR,
    XLSX_TEMPLATE_FILE,
    XLSX_TEMPLATE_FILE_COPY,
)
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

    def __delete_files(self, image_files_full_path: list[str]):
        for file_path in image_files_full_path:
            try:
                os.remove(file_path)
                logging.info(f"Deleted: {file_path}")
            except Exception as e:
                logging.info(f"Error deleting {file_path}: {str(e)}")

    def __save_pics(self, workbook: xw.Book, excel_starting_cell: str = "A1", image_width: int = 1000) -> None:
        """
        _summary_

        Parameters
        ----------
        workbook : xw.Book
            _description_
        excel_starting_cell : str, optional
            _description_, by default "A1"
        image_width : int, optional
            _description_, by default 1000

        Returns
        -------
        None
        """
        sheet = workbook.sheets[3]
        image_files = [f for f in os.listdir(SAVED_MAPS_IMAGES_DIR) if f.lower().endswith("png")]

        if not image_files:
            logging.info(f"No images found in {SAVED_MAPS_IMAGES_DIR}")
            return None

        # Set initial position
        left_position = sheet.range(excel_starting_cell).left
        top_position = sheet.range(excel_starting_cell).top

        image_files_full_path = []
        for i, image_file in enumerate(image_files):
            full_path = os.path.join(SAVED_MAPS_IMAGES_DIR, image_file)
            image_files_full_path.append(full_path)
            with Image.open(full_path) as img:
                orig_width, orig_height = img.size
                aspect_ratio = orig_height / orig_width
                calculated_height = image_width * aspect_ratio

            pic = sheet.pictures.add(
                full_path,
                left=left_position,
                top=top_position,
                width=image_width,
                height=calculated_height,
            )

            # Name the picture (optional)
            pic.name = f"MapImage_{i + 1}"
            # Update top position for next image
            top_position += calculated_height + 20
        sheet.range("A:A").column_width = image_width / 7

        # Autofit columns/rows if needed
        sheet.autofit()
        logging.info(f"Successfully inserted {len(image_files)} images")
        self.__delete_files(image_files_full_path)

        return None

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

            self.__save_pics(workbook)
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
