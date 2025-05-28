# -*- coding: utf-8 -*-
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):  # noqa: N802
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page count to each page (called at end of build)."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page = self.getPageNumber()
        text = "" if page <= 3 else f"Page {page - 3} of {page_count - 3}"
        self.setFont("Helvetica", 9)
        self.drawCentredString(0.5 * inch + (self._pagesize[0] - 1 * inch) / 2.0, 0.5 * inch - 0.3 * inch, text)
