# -*- coding: utf-8 -*-
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable

section_title_mapping = {
    "site_info_frame": "Site information",
    "on-on_frame": "On-site to on-site contamination",
    "on-off_frame": "On-site to off-site contamination",
    "off-on_frame": "Off-site to on-site contamination",
}

size_1 = 16
size_2 = 14
size_3 = 12


def create_custom_styles():
    """Create custom paragraph styles for the report"""
    styles = getSampleStyleSheet()

    # Add custom styles
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=size_1,
            leading=22,
            spaceAfter=12,
            alignment=1,  # Center aligned
        )
    )
    styles.add(
        ParagraphStyle(
            name="TOCHeader",
            parent=styles["Heading1"],
            fontSize=size_1,
            leading=20,
            spaceAfter=6,
            alignment=0,
            textColor=colors.black,
        )
    )

    styles.add(
        ParagraphStyle(
            name="toc_entry_section",
            parent=styles["Normal"],
            fontSize=size_2,
            leading=16,
            spaceAfter=6,
            leftIndent=0,
            textColor=colors.black,
        )
    )

    styles.add(
        ParagraphStyle(
            name="toc_entry_subsection",
            parent=styles["Normal"],
            fontSize=size_3,
            leading=16,
            spaceAfter=6,
            leftIndent=10,
            textColor=colors.black,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            parent=styles["Heading1"],
            fontSize=size_2,
            leading=20,
            spaceBefore=24,
            spaceAfter=12,
            textColor=colors.black,  # Darker blue
            alignment=0,  # Left aligned
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubSectionHeader",
            parent=styles["Heading3"],
            fontSize=size_3,
            leading=18,
            spaceBefore=18,
            spaceAfter=8,
            textColor=colors.black,
            alignment=0,
        )
    )

    return styles


def create_table_of_contents(sections: dict[str, list[tuple[str, str, str]]], styles) -> ListFlowable:
    """Create a table of contents flowable without bullets"""
    toc_items = []
    for section_title in sections:
        p = Paragraph(f'<a href="#{section_title}">{section_title}</a>', styles["toc_entry_section"])
        toc_items.append(ListItem(p, bulletText=""))
        for frame_tag, subsection_title, _ in sections[section_title]:
            if subsection_title != "":
                p = Paragraph(f'<a href="#{frame_tag}">{subsection_title}</a>', styles["toc_entry_subsection"])
                toc_items.append(ListItem(p, bulletText=""))

    return ListFlowable(toc_items, bulletType="bullet")


def create_table(
    frame_tag: str, ui_inp_vars: List[UIInpVariable], ui_calc_vars: Dict[str, UICalcVariable], styles
) -> Table:
    """Create a styled table for a group of input variables"""
    # Prepare table data
    table_data = [[Paragraph("<b>Description</b>", styles["Normal"]), Paragraph("<b>Value</b>", styles["Normal"])]]

    # Add input variables
    for var in ui_inp_vars:
        value = str(var.tk_var.get()) if hasattr(var.tk_var, "get") else ""
        table_data.append([Paragraph(var.text_val, styles["Normal"]), Paragraph(value, styles["Normal"])])

    # Add calculated risk if available
    if frame_tag in ui_calc_vars:
        calculated_risk = ui_calc_vars[frame_tag].tk_var.get()
        if calculated_risk:
            table_data.append(
                [
                    Paragraph("<b>Calculated Risk</b>", styles["Normal"]),
                    Paragraph(str(calculated_risk), styles["Normal"]),
                ]
            )

    # Create table with appropriate column widths
    table = Table(table_data, colWidths=[3 * inch, 2 * inch])

    # Apply table style
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E88E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]
    )

    # Add zebra striping for better readability
    for i, row in enumerate(table_data):
        if i > 0 and i % 2 == 0:
            style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F5F5F5"))

    table.setStyle(style)
    return table


def group_by_frame_tag(ui_inp_vars: Dict[str, UIInpVariable]) -> dict[str, list[UIInpVariable]]:
    """Group UIInpVariable objects by their frame_tag attribute."""
    ui_vars_grouped = {}
    for var in ui_inp_vars.values():
        if var.frame_tag not in ui_vars_grouped:
            ui_vars_grouped[var.frame_tag] = []
        ui_vars_grouped[var.frame_tag].append(var)
    return ui_vars_grouped


def create_pdf_report(
    ui_inp_vars: Dict[str, UIInpVariable],
    ui_calc_vars: Dict[str, UICalcVariable],
    output_filename: str,
    report_title: str = "Analysis Report",
) -> None:
    """Generate a PDF report with tables for each variable group"""
    # Create document with margins
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    # Get styles
    styles = create_custom_styles()
    story = []

    # Add report title
    story.append(Paragraph(report_title, styles["ReportTitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(PageBreak())

    # Group variables by frame tag and prepare TOC data
    ui_vars_grouped = group_by_frame_tag(ui_inp_vars)
    toc_sections = {}

    # Add table of contents header
    story.append(Paragraph("Contents", styles["TOCHeader"]))
    story.append(Spacer(1, 0.25 * inch))

    # First pass: Collect all section titles for TOC
    for frame_tag, vars_list in ui_vars_grouped.items():
        if "site_info_frame" in frame_tag:
            section_title = section_title_mapping["site_info_frame"]
        elif "on-on_frame" in frame_tag:
            section_title = section_title_mapping["on-on_frame"]
        elif "on-off_frame" in frame_tag:
            section_title = section_title_mapping["on-off_frame"]
        elif "off-on_frame" in frame_tag:
            section_title = section_title_mapping["off-on_frame"]
        else:
            raise ValueError(f"Unknown frame tag: {frame_tag}")

        subsection_title = vars_list[0].pdf_table_name
        if section_title not in toc_sections:
            toc_sections[section_title] = [(frame_tag, subsection_title, vars_list)]
        else:
            toc_sections[section_title].append((frame_tag, subsection_title, vars_list))

    # Add the TOC to the story
    story.append(create_table_of_contents(toc_sections, styles))
    story.append(PageBreak())

    for section_title in toc_sections:
        story.append(Paragraph(f'<a name="{section_title}"/>{section_title}', styles["SectionHeader"]))
        story.append(Spacer(1, 0.25 * inch))

        # Add each subsection
        for frame_tag, subsection_title, vars_list in toc_sections[section_title]:
            story.append(Paragraph(f'<a name="{frame_tag}"/>{subsection_title}', styles["SubSectionHeader"]))
            story.append(Spacer(1, 0.1 * inch))

            # Add table
            table = create_table(frame_tag, vars_list, ui_calc_vars, styles)
            story.append(table)

        story.append(PageBreak())

    doc.build(story)
