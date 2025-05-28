# -*- coding: utf-8 -*-
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from rss_islandr.core.config_parser import font_size_pdf_2, font_size_pdf_3


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
                fontSize=font_size_pdf_2,
                leftIndent=20,
                firstLineIndent=-20,
                spaceBefore=5,
            ),
            ParagraphStyle(
                name="TOCHeading2",
                fontName="Helvetica",
                fontSize=font_size_pdf_3,
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
