import shutil
from tkinter import messagebox

import ttkbootstrap as tb
import xlwings as xw

from rss_islandr.core.config_parser import REPORTS_DIR, XLSX_TEMPLATE_FILE, XLSX_TEMPLATE_FILE_COPY
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable, UISettings


class ExcelWriterBtnUI:
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

    def __on_button_click(self):
        values, positions = [], []
        for key in self.ui_inp_vars:
            try:
                position = self.ui_inp_vars[key].excel_cell
                value = self.ui_inp_vars[key].tk_var.get()
                positions.append(position)
                values.append(value)
                if key == "date_0_00":
                    print(position, value)
            except Exception:
                pass

        for key in self.ui_calc_vars:
            try:
                position = self.ui_calc_vars[key].excel_cell
                value = self.ui_calc_vars[key].tk_var.get()
                positions.append(position)
                values.append(f"{value}")
            except Exception:
                pass

        self.__write_to_excel(values, positions)

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

    def button(self, frame: tb.Frame):
        btn = tb.Button(
            frame,
            text="Write to Excel",
            command=self.__on_button_click,
        )

        return btn
