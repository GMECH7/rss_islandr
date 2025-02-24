import json
import shutil
from tkinter import messagebox, filedialog

import ttkbootstrap as tb
import xlwings as xw

from rss_islandr.core.config_parser import REPORTS_DIR, XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable, UISettings


class IOBtns:
    """
    Implementation of input-output buttons.
    ---------------------------------------
    1. Write to excel (reporting)
    2. Write to json file (scenario)
    3. Read from json file (scenario)
    """

    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        excel_file_template,
    ):
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.excel_file_template = excel_file_template

    def __access_vars(self):
        self.saved_scenario = {}
        self.positions, self.values = [], []
        for key in self.ui_inp_vars:
            try:
                position = self.ui_inp_vars[key].excel_cell
                value = self.ui_inp_vars[key].tk_var.get()
                self.positions.append(position)
                self.values.append(value)
                self.saved_scenario[key] = value
            except Exception:
                pass

        for key in self.ui_calc_vars:
            try:
                position = self.ui_calc_vars[key].excel_cell
                value = self.ui_calc_vars[key].tk_var.get()
                self.positions.append(position)
                self.values.append(f"{value}")
                self.saved_scenario[key] = f"{value}"
            except Exception:
                pass

    def __write_to_excel(self, values, positions):
        shutil.copy(XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY)
        try:
            app = xw.App(visible=False)
            try:
                workbook = xw.Book(XLSX_TEMPLATE_FILE_COPY)
            except FileNotFoundError:
                workbook = xw.Book()

            sheet = workbook.sheets[0]
            for value, position in zip(values, positions):
                if position is not None:
                    sheet.range(position).value = value

            workbook.save(XLSX_TEMPLATE_FILE_COPY)
            workbook.close()
            app.quit()
            shutil.copy(XLSX_TEMPLATE_FILE_COPY, "reporting.xlsx")
            messagebox.showinfo("Success", "Values written to Excel successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def __on_btn_click_xlsx_writer(self):
        """ """
        self.__access_vars()
        self.__write_to_excel(self.values, self.positions)

    def btn_write_xlsx(self, frame: tb.Frame) -> tb.Button:
        btn = tb.Button(frame, text="Write to Excel", command=self.__on_btn_click_xlsx_writer)

        return btn

    def __on_btn_click_scenario_writer(self):
        """ """
        self.__access_vars()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Scenario As",
        )

        if not file_path:  # User canceled the dialog
            return

        with open(file_path, "w") as scenario_file:
            json.dump(self.saved_scenario, scenario_file, indent=4)

    def btn_write_scenario(self, frame: tb.Frame) -> tb.Button:
        btn = tb.Button(frame, text="Save scenario", command=self.__on_btn_click_scenario_writer)
        return btn

    def __on_btn_click_scenario_reader(self):
        """ """
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="Open Scenario"
        )

        if not file_path:  # User canceled the dialog
            return
        with open(file_path, "r") as file:
            scenario_data = json.load(file)
        for ui_inp_var in self.ui_inp_vars:
            self.ui_inp_vars[ui_inp_var].tk_var.set(scenario_data[ui_inp_var])

    def btn_read_scenario(self, frame: tb.Frame) -> tb.Button:
        btn = tb.Button(frame, text="Read scenario", command=self.__on_btn_click_scenario_reader)
        return btn
