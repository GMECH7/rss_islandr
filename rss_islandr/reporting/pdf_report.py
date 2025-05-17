# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from rss_islandr.core.config_parser import ISLANDR_LOGO
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable

size_1 = 16
size_2 = 14
size_3 = 12

logging.basicConfig(level=logging.INFO)


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


class PDFReport:
    """
    Class to generate a PDF report with a Table of Contents (TOC).
    """

    section_title_mapping = {
        "site_info_frame": "Site information",
        "on-on_frame": "On-site to on-site contamination",
        "on-off_frame": "On-site to off-site contamination",
        "off-on_frame": "Off-site to on-site contamination",
    }

    def __init__(self, filename: str):
        self.filename = filename
        self.doc = CustomDocTemplate(
            filename,
            pagesize=letter,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        self.__init__create_custom_styles()
        self.story = []

    def __init__create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        self._styles = getSampleStyleSheet()

        self._styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self._styles["Title"],
                fontSize=size_1,
                leading=22,
                spaceAfter=12,
                alignment=1,  # center
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="ReportSubTitle",
                parent=self._styles["Normal"],
                fontSize=size_3,
                leading=0,
                spaceAfter=12,
                alignment=1,  # center
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="TOCHeader",
                parent=self._styles["Heading1"],
                fontSize=size_1,
                leading=20,
                spaceAfter=6,
                alignment=0,
                textColor=colors.black,
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self._styles["Heading1"],
                fontSize=size_2,
                leading=20,
                spaceBefore=24,
                spaceAfter=12,
                textColor=colors.black,
                alignment=0,
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="SubSectionHeader",
                parent=self._styles["Heading3"],
                fontSize=size_3,
                leading=18,
                spaceBefore=18,
                spaceAfter=8,
                textColor=colors.black,
                alignment=0,
            )
        )

    def add_page_number_footer(self, canvas: canvas.Canvas, doc, skip_count=3):
        page_num = canvas.getPageNumber()
        if page_num <= skip_count:
            return
        else:
            text = f"Page {page_num}"
            canvas.saveState()
            canvas.setFont("Helvetica", 9)
            canvas.drawCentredString(0.5 * inch + (doc.pagesize[0] - 1 * inch) / 2.0, 0.5 * inch - 0.3 * inch, text)
            canvas.restoreState()

    def __create_table(
        self, frame_tag: str, ui_inp_vars: list[UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]
    ) -> Table:
        """Tables generator"""

        table_data = [
            [Paragraph("<b>Description</b>", self._styles["Normal"]), Paragraph("<b>Value</b>", self._styles["Normal"])]
        ]
        for var in ui_inp_vars:
            val = var.tk_var.get() if hasattr(var.tk_var, "get") else ""
            table_data.append(
                [Paragraph(var.text_val, self._styles["Normal"]), Paragraph(str(val), self._styles["Normal"])]
            )

        if frame_tag in ui_calc_vars:
            cr = ui_calc_vars[frame_tag].tk_var.get()  # calculated risk
            if cr:
                table_data.append(
                    [
                        Paragraph("<b>Calculated Risk</b>", self._styles["Normal"]),
                        Paragraph(str(cr), self._styles["Normal"]),
                    ]
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

    def __group_by_frame_tag(self, ui_inp_vars: dict[str, UIInpVariable]) -> dict[str, list[UIInpVariable]]:
        """Group UIInpVariable objects by their frame_tag attribute."""
        grouped: dict[str, list[UIInpVariable]] = {}
        for v in ui_inp_vars.values():
            grouped.setdefault(v.frame_tag, []).append(v)
        return grouped

    def __call__(
        self,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        images_list: Optional[list[str]] = None,
        report_title: str = "Contamination Analysis Report",
    ) -> None:
        """PDF report generator"""
        date_now = datetime.datetime.now()
        date_str = date_now.strftime("%d %B %Y")
        logo = Image(ISLANDR_LOGO)  # Adjust size as needed
        # Title page
        self.story.append(Paragraph(report_title, self._styles["ReportTitle"]))
        self.story.append(Spacer(1, 0.5 * inch))
        self.story.append(logo)  # add image here
        self.story.append(Spacer(1, 0.5 * inch))  # optional spacing
        self.story.append(Paragraph(date_str, self._styles["ReportSubTitle"]))
        self.story.append(Spacer(1, 0.25 * inch))
        self.story.append(PageBreak())

        # TOC header + the TOC itself
        self.story.append(Paragraph("Contents", self._styles["TOCHeader"]))
        self.story.append(Spacer(1, 0.25 * inch))
        self.story.append(self.doc.toc)
        self.story.append(PageBreak())

        # Build mapping of sections→subsections
        grouped = self.__group_by_frame_tag(ui_inp_vars)
        toc_sections: dict[str, list] = {}
        for ft, vars_list in grouped.items():
            if "site_info_frame" in ft:
                sec = self.section_title_mapping["site_info_frame"]
            elif "on-on_frame" in ft:
                sec = self.section_title_mapping["on-on_frame"]
            elif "on-off_frame" in ft:
                sec = self.section_title_mapping["on-off_frame"]
            elif "off-on_frame" in ft:
                sec = self.section_title_mapping["off-on_frame"]
            else:
                raise ValueError(f"Unknown frame tag: {ft}")

            sub = vars_list[0].pdf_table_name
            toc_sections.setdefault(sec, []).append((ft, sub, vars_list))

        # Add sections + subsections + tables
        for sec_title, entries in toc_sections.items():
            anchor_name = sec_title.replace("", "_")[:50]
            self.story.append(Paragraph(f'<a name="{anchor_name}"/>{sec_title}', self._styles["SectionHeader"]))

            for ft, sub_title, vars_list in entries:
                anchor_name = sub_title.replace("", "_")[:50]
                self.story.append(Paragraph(f'<a name="{anchor_name}"/>{sub_title}', self._styles["SubSectionHeader"]))
                self.story.append(Spacer(1, 0.1 * inch))
                self.story.append(self.__create_table(ft, vars_list, ui_calc_vars))
            self.story.append(PageBreak())

        if images_list:
            self.story.append(Paragraph("Figures", self._styles["SectionHeader"]))
            self.story.append(Spacer(1, 0.2 * inch))

            max_width = 5.5 * inch  # or whatever fits your page layout

            for img_path in images_list:
                try:
                    img_reader = ImageReader(img_path)
                    img_width, img_height = img_reader.getSize()
                    aspect = img_height / float(img_width)
                    scaled_height = max_width * aspect

                    img = Image(img_path, width=max_width, height=scaled_height)
                    img.hAlign = "CENTER"
                    self.story.append(img)
                    self.story.append(Spacer(1, 0.2 * inch))
                except Exception:
                    logging.info(f"Error : Image {img_path} was not included in the PDF report")

            self.story.append(PageBreak())

        # two‐pass build to resolve TOC page numbers
        self.doc.multiBuild(self.story, onLaterPages=self.add_page_number_footer)
