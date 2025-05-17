# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable

# -- mappings & sizes -------------------------------------------------------

section_title_mapping = {
    "site_info_frame": "Site information",
    "on-on_frame": "On-site to on-site contamination",
    "on-off_frame": "On-site to off-site contamination",
    "off-on_frame": "Off-site to on-site contamination",
}

size_1 = 16
size_2 = 14
size_3 = 12

# -- custom DocTemplate with TOC support ------------------------------------


class CustomDocTemplate(SimpleDocTemplate):
    """
    Custom DocTemplate that supports a Table of Contents (TOC).
    """

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        # create TOC object here so we can inject it in story
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            ParagraphStyle(
                name="TOCHeading1",
                fontName="Helvetica-Bold",
                fontSize=size_2,
                leftIndent=20,
                firstLineIndent=-20,
                spaceBefore=5,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                fontName="Helvetica",
                fontSize=size_3,
                leftIndent=40,
                firstLineIndent=-20,
                spaceBefore=0,
            ),
        ]
        self.section_count = 0
        self.subsection_count = 0

    def afterFlowable(self, flowable):  # noqa: N802
        """
        NOTE: This method OVERRIDES the afterFlowable method of SimpleDocTemplate.

        It is automatically called after each flowable is drawn.
        It is used to register TOC entries for our SectionHeader & SubSectionHeader.
        """
        if hasattr(flowable, "style") and hasattr(flowable, "getPlainText"):
            style_name = flowable.style.name
            text = flowable.getPlainText()
            page_num = self.canv.getPageNumber()

            # Create a unique anchor/bookmark name
            bookmark_name = text.replace(" ", "_").replace("&", "").replace("<", "").replace(">", "")[:50]

            # Register the bookmark on the canvas
            self.canv.bookmarkPage(bookmark_name)

            # Register the TOC entry with the same anchor name
            if style_name == "SectionHeader":
                self.notify("TOCEntry", (0, text, page_num, bookmark_name))
            elif style_name == "SubSectionHeader":
                self.notify("TOCEntry", (1, text, page_num, bookmark_name))


def create_custom_styles():
    """Create custom paragraph styles for the report"""
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=size_1,
            leading=22,
            spaceAfter=12,
            alignment=1,  # center
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
            name="SectionHeader",
            parent=styles["Heading1"],
            fontSize=size_2,
            leading=20,
            spaceBefore=24,
            spaceAfter=12,
            textColor=colors.black,
            alignment=0,
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


# -- table generator --------------------------------------------------------


def create_table(
    frame_tag: str, ui_inp_vars: list[UIInpVariable], ui_calc_vars: dict[str, UICalcVariable], styles
) -> Table:
    """Tables generator"""

    table_data = [[Paragraph("<b>Description</b>", styles["Normal"]), Paragraph("<b>Value</b>", styles["Normal"])]]
    for var in ui_inp_vars:
        val = var.tk_var.get() if hasattr(var.tk_var, "get") else ""
        table_data.append([Paragraph(var.text_val, styles["Normal"]), Paragraph(str(val), styles["Normal"])])

    if frame_tag in ui_calc_vars:
        cr = ui_calc_vars[frame_tag].tk_var.get()  # calculated risk
        if cr:
            table_data.append(
                [Paragraph("<b>Calculated Risk</b>", styles["Normal"]), Paragraph(str(cr), styles["Normal"])]
            )

    tbl = Table(table_data, colWidths=[3 * inch, 2 * inch])
    tbl_style = TableStyle(
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
    # zebra striping
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            tbl_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F5F5F5"))

    tbl.setStyle(tbl_style)
    return tbl


# -- grouping helper --------------------------------------------------------


def group_by_frame_tag(ui_inp_vars: dict[str, UIInpVariable]) -> dict[str, list[UIInpVariable]]:
    """Group UIInpVariable objects by their frame_tag attribute."""
    grouped: dict[str, list[UIInpVariable]] = {}
    for v in ui_inp_vars.values():
        grouped.setdefault(v.frame_tag, []).append(v)
    return grouped


# -- main PDF generator -----------------------------------------------------


def create_pdf_report(
    ui_inp_vars: dict[str, UIInpVariable],
    ui_calc_vars: dict[str, UICalcVariable],
    output_filename: str,
    report_title: str = "Analysis Report",
) -> None:
    """PDF report generator"""
    doc = CustomDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = create_custom_styles()
    story = []

    # Title page
    story.append(Paragraph(report_title, styles["ReportTitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(PageBreak())

    # TOC header + the TOC itself
    story.append(Paragraph("Contents", styles["TOCHeader"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(doc.toc)
    story.append(PageBreak())

    # Build mapping of sections→subsections
    grouped = group_by_frame_tag(ui_inp_vars)
    toc_sections: dict[str, list] = {}
    for ft, vars_list in grouped.items():
        if "site_info_frame" in ft:
            sec = section_title_mapping["site_info_frame"]
        elif "on-on_frame" in ft:
            sec = section_title_mapping["on-on_frame"]
        elif "on-off_frame" in ft:
            sec = section_title_mapping["on-off_frame"]
        elif "off-on_frame" in ft:
            sec = section_title_mapping["off-on_frame"]
        else:
            raise ValueError(f"Unknown frame tag: {ft}")

        sub = vars_list[0].pdf_table_name
        toc_sections.setdefault(sec, []).append((ft, sub, vars_list))

    # Add sections + subsections + tables
    for sec_title, entries in toc_sections.items():
        anchor_name = sec_title.replace("", "_")[:50]
        story.append(Paragraph(f'<a name="{anchor_name}"/>{sec_title}', styles["SectionHeader"]))

        for ft, sub_title, vars_list in entries:
            anchor_name = sub_title.replace("", "_")[:50]
            story.append(Paragraph(f'<a name="{anchor_name}"/>{sub_title}', styles["SubSectionHeader"]))
            story.append(Spacer(1, 0.1 * inch))
            story.append(create_table(ft, vars_list, ui_calc_vars, styles))
        story.append(PageBreak())

    # two‐pass build to resolve TOC page numbers
    doc.multiBuild(story)
