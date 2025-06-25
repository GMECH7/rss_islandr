# -*- coding: utf-8 -*-

import datetime
import logging
from typing import Optional

import ttkbootstrap as tb
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from rss_islandr.core.config_parser import ISLANDR_LOGO, font_size_pdf_1, font_size_pdf_2, font_size_pdf_3
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable
from rss_islandr.core.helpers import extract_dicts_from_string
from rss_islandr.reporting.custom_doc_template import CustomDocTemplate
from rss_islandr.reporting.numbered_canvas import NumberedCanvas

logging.basicConfig(level=logging.INFO)


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
        self._pages_to_omit = 3  # cover + TOC will be omitted from page numbering
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
        self.__table_header_color = "#1E88E5"
        self._styles = getSampleStyleSheet()

        self._styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self._styles["Title"],
                fontSize=font_size_pdf_1,
                leading=22,
                spaceAfter=12,
                alignment=1,  # center
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="ReportSubTitle",
                parent=self._styles["Normal"],
                fontSize=font_size_pdf_3,
                leading=0,
                spaceAfter=12,
                alignment=1,  # center
            )
        )
        self._styles.add(
            ParagraphStyle(
                name="TOCHeader",
                parent=self._styles["Heading1"],
                fontSize=font_size_pdf_1,
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
                fontSize=font_size_pdf_2,
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
                parent=self._styles["Heading2"],
                fontSize=font_size_pdf_3,
                leading=18,
                spaceBefore=18,
                spaceAfter=8,
                textColor=colors.black,
                alignment=0,
            )
        )

    def __create_table(
        self, frame_tag: str, ui_inp_vars: list[UIInpVariable], ui_calc_vars: dict[str, UICalcVariable]
    ) -> Table:
        """Tables generator"""

        table_data = [
            [Paragraph("<b>Description</b>", self._styles["Normal"]), Paragraph("<b>Value</b>", self._styles["Normal"])]
        ]
        for var in ui_inp_vars:
            val = var.tk_var.get() if hasattr(var.tk_var, "get") else ""
            if var.text_val == "Latitude" or var.text_val == "Longitude":
                val = f"{float(val):.4f}"

            table_data.append([Paragraph(var.text_val, self._styles["Normal"]), Paragraph(val, self._styles["Normal"])])

        if frame_tag in ui_calc_vars:
            calc_risk = ui_calc_vars[frame_tag].tk_var.get()
            if calc_risk:
                table_data.append(
                    [
                        Paragraph("<b>Calculated Risk [%]</b>", self._styles["Normal"]),
                        Paragraph(f"{100 * float(calc_risk):.2f}", self._styles["Normal"]),
                    ]
                )

        tbl = Table(table_data, colWidths=[3 * inch, 2 * inch])
        tbl_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(self.__table_header_color)),
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

    def __add__title_toc_to_story(self, report_title: str) -> None:
        """Add title and TOC to the story"""
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

    def __add__figures_to_story(self, images_list: list[str]) -> None:
        """Add figures to the story"""

        self.story.append(Paragraph("Figures", self._styles["SectionHeader"]))
        self.story.append(Spacer(1, 0.2 * inch))

        max_width = 5.5 * inch

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
                logging.debug(f"Error : Image {img_path} was not included in the PDF report")

        self.story.append(PageBreak())

    def __add_polygons_to_story(self, polygons_data_tkvar: tb.StringVar):
        """
        Add polygon data table to the report

        Parameters
        ----------
        polygons_data_tkvar : tb.StringVar
            Representation of the polygons dictionary.
        """
        polygons_data = extract_dicts_from_string(polygons_data_tkvar.get())

        try:
            # Add section header
            self.story.append(Paragraph("Polygon Data", self._styles["SectionHeader"]))
            self.story.append(Spacer(1, 0.2 * inch))

            # Extract polygon type for header
            for polygon_dict in polygons_data:
                poly_type = polygon_dict.get("type", "polygon:unknown")
                clean_type = poly_type.replace("polygon:", "").capitalize()

                self.story.append(Paragraph(clean_type, self._styles["SubSectionHeader"]))
                self.story.append(Spacer(1, 0.1 * inch))

                # Create table data with headers
                table_data = [["Point", "Longitude", "Latitude", "Area (km²)", "Nodes"]]

                coordinates = polygon_dict.get("coordinates", [])
                area = polygon_dict.get("area_km2", 0)
                nodes = polygon_dict.get("node_count", 0)

                # Add each coordinate pair with point numbering
                for point_idx, coord in enumerate(coordinates, 1):
                    if len(coord) >= 2:  # Ensure we have both lat and long
                        if point_idx == 1:  # First row shows all info
                            table_data.append(
                                [
                                    str(point_idx),
                                    f"{coord[0]:.6f}",
                                    f"{coord[1]:.6f}",
                                    f"{float(area):,.2f}",
                                    str(nodes),
                                ]
                            )
                        else:  # Subsequent rows just show coordinates
                            table_data.append([str(point_idx), f"{coord[0]:.6f}", f"{coord[1]:.6f}", "", ""])

                # Create the table
                tbl = Table(table_data, colWidths=[0.6 * inch, 1.2 * inch, 1.2 * inch, 1 * inch, 0.6 * inch])

                # Add style to table
                tbl_style = TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(self.__table_header_color)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ("SPAN", (3, 1), (3, len(coordinates))),  # Span area
                        ("SPAN", (4, 1), (4, len(coordinates))),  # Span node count
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )

                # Zebra striping
                for i in range(1, len(table_data)):
                    if i % 2 == 0:
                        tbl_style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F5F5F5"))

                tbl.setStyle(tbl_style)
                self.story.append(tbl)
                self.story.append(Spacer(1, 0.3 * inch))

        except Exception as e:
            logging.error(f"Error processing polygon data: {e}")
            self.story.append(Paragraph("Error displaying polygon data", self._styles["Normal"]))

    # Update the __call__ method to use the new polygon method
    def __call__(
        self,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        polygons_data: tb.StringVar,
        images_list: Optional[list[str]] = None,
        report_title: str = "Contamination Analysis Report",
    ) -> None:
        """
        PDF report generator

        Parameters
        ----------
        ui_inp_vars : dict[str, UIInpVariable]
            _description_
        ui_calc_vars : dict[str, UICalcVariable]
            _description_
        polygons_data : tb.StringVar
            _description_
        images_list : Optional[list[str]], optional
            _description_, by default None
        report_title : str, optional
            _description_, by default "Contamination Analysis Report"

        Raises
        ------
        ValueError
            _description_
        """
        self.__add__title_toc_to_story(report_title)

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
            self.__add__figures_to_story(images_list)

        if polygons_data.get() != "":
            self.__add_polygons_to_story(polygons_data)

        from functools import partial

        canvasmaker = partial(NumberedCanvas, pages_to_omit=self._pages_to_omit)
        self.doc.multiBuild(self.story, canvasmaker=canvasmaker)
