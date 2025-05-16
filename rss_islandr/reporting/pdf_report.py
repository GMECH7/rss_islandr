from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable


def create_table(ui_variables: Dict[str, UIInpVariable]) -> Table:
    """
    Converts UIInpVariable data into a ReportLab table.
    Left column: text_val (description).
    Right column: val_default or tk_var value.
    Rows are sorted by Excel cell row number (e.g., A10 → row 10).
    """
    # Step 1: Extract and prepare data
    table_data = []
    for var in ui_variables.values():
        if not var.excel_cell:
            continue  # Skip variables without Excel cell assignment

        # Parse Excel cell (e.g., "A10" → row 10)
        col_letter = "".join([c for c in var.excel_cell if c.isalpha()])
        row_number = int("".join([c for c in var.excel_cell if c.isdigit()]))

        # Get value (prioritize val_default; fall back to tk_var if needed)
        value = var.val_default if var.val_default else str(var.tk_var.get()) if hasattr(var.tk_var, "get") else ""

        table_data.append({"row": row_number, "text_val": var.text_val, "value": value})

    # Step 2: Sort by Excel row number
    table_data.sort(key=lambda x: x["row"])

    # Step 3: Build grid (left=text_val, right=value)
    grid = [["Description", "Value"]]  # Header row
    for item in table_data:
        grid.append([item["text_val"], item["value"]])

    # Step 4: Create ReportLab Table
    table = Table(grid)
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header background
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
    table.setStyle(style)

    return table


def create_pdf_report(ui_variables: Dict[str, UIInpVariable], output_filename):
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
    table = create_table(ui_variables)
    # Build the document
    doc.build([table])
