import contextlib
import json
import logging
import math
import os
import re
import tkinter as tk
from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import filedialog

import ttkbootstrap as tb
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XlImage
from PIL import Image, ImageTk

from rss_islandr.core.config_parser import (
    STATIC_DIR,
    XLSX_TEMPLATE_FILE,
)
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable
from rss_islandr.core.helpers import extract_dicts_from_string
from rss_islandr.core.logger_config import logger_decorator
from rss_islandr.reporting import PDFReport
from rss_islandr.ui import dialogs

logger = logging.getLogger(__name__)


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
            logger.debug(f"Error accessing {key}: {ex}")

    def access_vars(self):
        """Access all input and calculated UI-variables"""
        #: Access input variables
        for key in self.ui_inp_vars:
            self.__access_vars_loop(key, self.ui_inp_vars)
        #: Access calculated variables
        for key in self.ui_calc_vars:
            self.__access_vars_loop(key, self.ui_calc_vars)

    @staticmethod
    def add_maps_prompt(report_type: str) -> list[str]:
        """
        Prompt to ask user if they want to add maps images to the Excel/PDF report.
        """
        add_maps = dialogs.ask_yes_no("Add Maps", f"Do you want to add maps images to the {report_type} report?")

        if add_maps:
            selected_image_files = list(
                filedialog.askopenfilenames(
                    title="Select Map Images", filetypes=[("PNG Images", "*.png"), ("JPEG Images", "*.jpeg")]
                )
            )
        else:
            selected_image_files = []
            dialogs.show_info("No Images Selected", "No images were selected. Proceeding without maps.")

        return selected_image_files

    @abstractmethod
    def on_btn_click(self, *args):
        """ """

    @abstractmethod
    def btn(self, *args):
        """ """


class ExportExcelReportBtn(IOBtns):
    """Implementation of button for exporting to excel file"""

    #: Sheet positions in the template (see `report_template.xlsx`)
    MAPS_SHEET_POS = 3
    COORDINATES_SHEET_POS = 4

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        map_polygons_tb = kwargs.get("map_polygons_tb", tb.StringVar(value=""))
        self._polygons_data = map_polygons_tb

    @staticmethod
    def __to_cell_value(value):
        """
        Convert a UI text value to the type it should have in the sheet.

        Numbers and ISO dates (as given by the date widgets) are stored as numbers/dates and not as text,
        so that the cell formats of the template (e.g. percentage for the risk) are applied.
        """
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        if re.fullmatch(r"-?\d+\.\d+(e-?\d+)?", value):
            return float(value)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            with contextlib.suppress(ValueError):
                return datetime.strptime(value, "%Y-%m-%d")
        return value

    def __save_maps_as_imgs(
        self,
        workbook: Workbook,
        selected_image_files: list[str],
        image_width: int = 1000,
    ) -> None:
        """
        Insert map images into the maps sheet of the Excel workbook, one below the other.

        Parameters
        ----------
        workbook : Workbook
            The Excel workbook to insert images into
        selected_image_files : list[str]
            List of selected image file paths
        image_width : int, optional
            Fixed width for all images in points (default: 1000)
        """
        sheet = workbook.worksheets[self.MAPS_SHEET_POS]
        points_to_pixels = 96 / 72
        row_height_pixels = 20  # Default row height of 15 points
        gap_pixels = 20 * points_to_pixels

        width_pixels = image_width * points_to_pixels
        next_row = 1
        for image_file in selected_image_files:
            image = XlImage(os.path.abspath(str(image_file)))
            aspect_ratio = image.height / image.width
            image.width = width_pixels
            image.height = width_pixels * aspect_ratio
            sheet.add_image(image, f"A{next_row}")
            next_row += math.ceil((image.height + gap_pixels) / row_height_pixels)
        sheet.column_dimensions["A"].width = image_width / 7
        logger.debug(f"Successfully inserted {len(selected_image_files)} images")

    def __save_polygons_data(self, workbook: Workbook):
        """
        Save polygons data to the coordinates sheet of the Excel workbook.

        Parameters
        ----------
        workbook : Workbook
            The Excel workbook to save polygons data into.
        """
        sheet = workbook.worksheets[self.COORDINATES_SHEET_POS]
        map_polygons_tb = extract_dicts_from_string(self._polygons_data.get())
        logger.debug(f"Polygons data to save: {map_polygons_tb}")
        row_idx = 1
        for polygon in map_polygons_tb:
            row_idx += 1
            coords = polygon.get("coordinates", [])
            sheet[f"E{row_idx}"] = polygon.get("area_km2", "")
            for j, coord in enumerate(coords):
                sheet[f"A{row_idx}"] = polygon.get("name", "")
                sheet[f"B{row_idx}"] = j + 1
                sheet[f"C{row_idx}"] = coord[0]
                sheet[f"D{row_idx}"] = coord[1]
                row_idx += 1

    @logger_decorator
    def on_btn_click(self):
        """ """
        self.access_vars()
        selected_image_files = self.add_maps_prompt("excel")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("XLSX files", "*.xlsx"), ("All files", "*.*")],
            title="Save Scenario As",
        )
        if not file_path:  # User canceled the dialog
            return

        try:
            workbook = load_workbook(XLSX_TEMPLATE_FILE)

            scenario_sheets = {"on-on": 0, "on-off": 1, "off-on": 2}
            for sheet_name_key, sheet_pos in scenario_sheets.items():
                sheet = workbook.worksheets[sheet_pos]
                for position, value in self.xlsx_sheet_pos_vals[sheet_name_key]:
                    logger.debug(f"Writing {value} to {sheet.title} {position}")
                    if position is not None:
                        sheet[position] = self.__to_cell_value(value)

            self.__save_maps_as_imgs(workbook, selected_image_files)
            self.__save_polygons_data(workbook)
            workbook.save(file_path)
            dialogs.show_info("Success", "Values written to Excel successfully!")
        except Exception as e:
            dialogs.show_error("Error", f"An error occurred: {e}")

    @logger_decorator
    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Write to Excel", command=self.on_btn_click)

        return btn


class ExportPDFReportBtn(IOBtns):
    """Implementation of button for exporting to pdf file"""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        map_polygons_tb = kwargs.get("map_polygons_tb", tb.StringVar(value=""))
        self.map_polygons_tb = map_polygons_tb

    @logger_decorator
    def on_btn_click(self):
        """ """
        selected_image_files = self.add_maps_prompt("pdf")
        if len(selected_image_files) == 0:
            selected_image_files = None

        self.access_vars()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report As",
        )
        if not file_path:  # User canceled the dialog
            return

        try:
            pdf_report = PDFReport(file_path)
            pdf_report(self.ui_inp_vars, self.ui_calc_vars, self.map_polygons_tb, selected_image_files)
            dialogs.show_info("Success", "PDF report exported!")
        except Exception as e:
            dialogs.show_error("Error", f"An error occurred: {e}")

    @logger_decorator
    def btn(self, frame: tb.Frame):
        """ """


class ExportScenarioBtn(IOBtns):
    """Implementation of button for exporting a scenario to a json file."""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        map_polygons_tb = kwargs.get("map_polygons_tb", tb.StringVar(value=""))
        self.map_polygons_tb = map_polygons_tb

    @logger_decorator
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
            self.saved_scenario.update({"polygons_data": self.map_polygons_tb.get()})
            with open(file_path, "w") as scenario_file:
                json.dump(self.saved_scenario, scenario_file, indent=4)
                dialogs.show_info("Success", "Scenario values exported!")
        except Exception as e:
            dialogs.show_error("Error", f"An error occurred: {e}")

    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Save scenario", command=self.on_btn_click)
        return btn


class ImportScenarioBtn(IOBtns):
    """Implementation of button for importing a scenario from a json file."""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        self.map_ui = kwargs.get("map_ui")
        map_polygons_tb = kwargs.get("map_polygons_tb", tb.StringVar(value=""))
        self.map_polygons_tb = map_polygons_tb

    @logger_decorator
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
            self.map_polygons_tb.set(scenario_data.get("polygons_data", ""))

            if self.map_ui is None:
                raise ValueError("Map UI is not initialized.")
            else:
                self.map_ui.update_polygons_from_stringvar()  # Explicit update
                self.map_ui.update_coordinates()
            dialogs.show_info("Success", "Scenario values imported!")
        except Exception as e:
            dialogs.show_error("Error", f"An error occurred: {e}")

    @logger_decorator
    def btn(self, frame: tb.Frame) -> tb.Button:
        """ """
        btn = tb.Button(frame, text="Read scenario", command=self.on_btn_click)
        return btn


class PopupImage(IOBtns):
    """Implementation of button for opening a popup window presenting an image."""

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
        resized_image = self.original_image.resize((1800, 908), Image.LANCZOS)  # type: ignore
        self.photo = ImageTk.PhotoImage(resized_image)

        label = tk.Label(self.popup_window, image=self.photo)
        label.pack(padx=10, pady=10)

    @logger_decorator
    def on_btn_click(self, frame: tb.Frame):
        """Opens or closes the popup window with the image."""
        if self.popup_window and tk.Toplevel.winfo_exists(self.popup_window):
            self.popup_window.destroy()  # Close if already open
            self.popup_window = None
        else:
            self.__show_popup(frame)  # Open if closed

    def btn(self):
        pass
