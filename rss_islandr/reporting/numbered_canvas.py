from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas that adds page numbers to the PDF.
    """

    def __init__(self, *args, **kwargs):
        """
        **kwargs**:
            - **pages_to_omit**: Number of pages to skip before starting page numbering (default is 0).
        """
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._pages_to_omit = kwargs.get("pages_to_omit", 0)

        self._page_number = 0

    def showPage(self):
        """
        Override showPage to increment page number and draw it.
        """
        self._page_number += 1
        self.draw_page_number()
        canvas.Canvas.showPage(self)

    def draw_page_number(self):
        """Draw page number at bottom of page, skipping cover pages"""
        # Skip first 3 pages (cover + TOC)
        if self._page_number > self._pages_to_omit:
            self.saveState()
            self.setFont("Helvetica", 9)
            text = f"Page {self._page_number - self._pages_to_omit}"
            # Center the page number at bottom
            x = self._pagesize[0] / 2
            y = 0.5 * inch - 0.3 * inch
            self.drawCentredString(x, y, text)
            self.restoreState()

    def save(self):
        """Standard save - page numbers are added during showPage"""
        canvas.Canvas.save(self)
