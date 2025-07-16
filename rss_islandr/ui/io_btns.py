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
    STATIC_DIR,
    XLSX_TEMPLATE_FILE,
    XLSX_TEMPLATE_FILE_COPY,
)
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable
from rss_islandr.core.helpers import extract_dicts_from_string
from rss_islandr.reporting import PDFReport

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

    @staticmethod
    def add_maps_prompt(report_type: str) -> list[str]:
        """
        Prompt to ask user if they want to add maps images to the Excel/PDF report.
        """
        add_maps = messagebox.askyesno("Add Maps", f"Do you want to add maps images to the {report_type} report?")

        if add_maps:
            selected_image_files = list(
                filedialog.askopenfilenames(
                    title="Select Map Images", filetypes=[("PNG Images", "*.png"), ("JPEG Images", "*.jpeg")]
                )
            )
        else:
            selected_image_files = []
            messagebox.showinfo("No Images Selected", "No images were selected. Proceeding without maps.")

        return selected_image_files

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

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], *args, **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        polygons_data = kwargs.get("polygons_data", tb.StringVar(value=""))
        self._polygons_data = polygons_data

    def __save_maps_as_imgs(
        self,
        workbook: xw.Book,
        selected_image_files: list[str],
        excel_starting_cell: str = "A1",
        image_width: int = 1000,
    ) -> None:
        """
        Implementation of method to insert map images into the Excel workbook.

        Parameters
        ----------
        workbook : xw.Book
            The Excel workbook to insert images into
        selected_image_files : list[str]
            List of selected image file paths
        excel_starting_cell : str, optional
            Starting cell position for images (default: "A1")
        image_width : int, optional
            Fixed width for all images in points (default: 1000)
        """
        sheet = workbook.sheets[3]

        left_position = sheet.range(excel_starting_cell).left
        top_position = sheet.range(excel_starting_cell).top

        for i, image_file in enumerate(selected_image_files):
            full_path = os.path.abspath(str(image_file))

            with Image.open(full_path) as img:
                orig_width, orig_height = img.size
                aspect_ratio = orig_height / orig_width
                image_height_calc = image_width * aspect_ratio

            pic = sheet.pictures.add(
                full_path,
                left=left_position,
                top=top_position,
                width=image_width,
                height=image_height_calc,
            )

            # Name the picture (optional)
            pic.name = f"MapImage_{i + 1}"
            # Update top position for next image
            top_position += image_height_calc + 20
        sheet.range("A:A").column_width = image_width / 7

        # Autofit columns/rows if needed
        sheet.autofit()
        logging.debug(f"Successfully inserted {len(selected_image_files)} images")

        return None

    def __save_polygons_data(self, workbook: xw.Book):
        """
        Save polygons data to the Excel workbook.

        Parameters
        ----------
        workbook : xw.Book
            The Excel workbook to save polygons data into.
        """
        sheet = workbook.sheets[4]
        polygons_data = extract_dicts_from_string(self._polygons_data.get())

        row_idx = 1
        for i in range(len(polygons_data)):
            row_idx += 1
            coords = polygons_data[i].get("coordinates", [])
            sheet.range(f"E{row_idx}").value = polygons_data[i].get("area_km2", "")
            for j, coord in enumerate(coords):
                sheet.range(f"A{row_idx}").value = polygons_data[i].get("name", "")
                sheet.range(f"B{row_idx}").value = j + 1
                sheet.range(f"C{row_idx}").value = coord[0]
                sheet.range(f"D{row_idx}").value = coord[1]
                row_idx += 1

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

            self.__save_maps_as_imgs(workbook, selected_image_files)
            self.__save_polygons_data(workbook)
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


class ExportPDFReportBtn(IOBtns):
    """Implementation of button for exporting to pdf file"""

    def __init__(self, ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], *args, **kwargs):
        super().__init__(ui_inp_vars, ui_calc_vars)
        polygons_data = kwargs.get("polygons_data", tb.StringVar(value=""))
        self.polygons_data = polygons_data

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
            pdf_report(self.ui_inp_vars, self.ui_calc_vars, self.polygons_data, selected_image_files)
            messagebox.showinfo("Success", "PDF report exported!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def btn(self, frame: tb.Frame):
        """ """
        pass


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
