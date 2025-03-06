import ttkbootstrap as tb
from PIL import Image, ImageTk


class HomeUI:
    def __init__(self, parent_navbar_frame: tb.Frame, parent_frame: tb.Frame):
        """
        Home page

        Parameters
        ----------
        parent_navbar_frame : tb.Frame
            Parent navbar frame.
        parent_frame : tb.Frame
            Parent frame.
        """
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame

    def ui(self, islandr_logo_img):
        """No functionality is added in the main page."""

        # Set the image as background
        background_label = tb.Label(self.__parent_frame, image=islandr_logo_img)
        background_label.pack(pady=160)
