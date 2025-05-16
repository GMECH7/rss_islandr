# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable


def create_table(frame_tag, ui_inp_vars: list[UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]) -> Table:
    """ """
    table_data = []
    for var in ui_inp_vars:
        value = var.tk_var.get() if hasattr(var.tk_var, "get") else ""
        table_data.append([var.text_val, value])

    calculated_risk = ui_calc_vars[frame_tag].tk_var.get() if frame_tag in ui_calc_vars else ""
    if calculated_risk != "":
        table_data.append(["Risk", ""])  # Empty row for spacing

    pdf_table_name = var.pdf_table_name
    grid = [
        [pdf_table_name, ""],  # Header spans both columns (merged later)
        ["Description", "Value"],  # Sub-header (column labels)
    ]
    for item in table_data:
        grid.append(item)

    table = Table(grid)
    style = TableStyle(
        [
            ("SPAN", (0, 0), (1, 0)),
            ("BACKGROUND", (0, 0), (-1, 1), colors.grey),  # Header + sub-header
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
    table.setStyle(style)

    return table


def group_by_frame_tag(ui_inp_vars: dict[str, UIInpVariable]) -> dict[str, list[UIInpVariable]]:
    """Group UIInpVariable objects by their frame_tag attribute."""

    ui_vars_grouped_by_frame_tag = {}
    for var_str in ui_inp_vars:
        var = ui_inp_vars[var_str]
        if var.frame_tag not in ui_vars_grouped_by_frame_tag:
            ui_vars_grouped_by_frame_tag[var.frame_tag] = [var]
        else:
            ui_vars_grouped_by_frame_tag[var.frame_tag].append(var)

    return ui_vars_grouped_by_frame_tag


def create_pdf_report(ui_inp_vars: dict[str, UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], output_filename):
    # Create a document with letter size pages
    doc = SimpleDocTemplate(output_filename, pagesize=letter)

    # Container for the 'Flowable' objects (elements of the document)
    story = []

    # Get the default sample styles
    styles = getSampleStyleSheet()

    # Add a title
    title = Paragraph("My First PDF Report", styles["Title"])
    story.append(title)

    # Add some space
    story.append(Spacer(1, 0.25 * inch))

    # Add some content
    text = "This is a minimal working example of a PDF created with ReportLab."
    story.append(Paragraph(text, styles["Normal"]))

    # Add more space and another paragraph
    story.append(Spacer(1, 0.25 * inch))
    text = "ReportLab is a powerful library for creating PDF documents programmatically."
    story.append(Paragraph(text, styles["Normal"]))
    ui_vars_grouped_by_frame_tag = group_by_frame_tag(ui_inp_vars)

    all_tables = []
    for frame_tag in ui_vars_grouped_by_frame_tag:
        table = create_table(frame_tag, ui_vars_grouped_by_frame_tag[frame_tag], ui_calc_vars)
        all_tables.append(table)

    # Build the document
    doc.build(all_tables)
