# -*- coding: utf-8 -*-
import ttkbootstrap as tb


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
        ui_settings: UISettings
        """
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame

    def ui(self, islandr_logo_img):
        """No functionality is added in the main page."""
        background_label = tb.Label(self.__parent_frame, image=islandr_logo_img)
        background_label.pack(pady=160)

        disclaimer_label = tb.Label(
            self.__parent_frame,
            text="Funded by the European Union, Grant agreement n°1001112889",
            style="General.TLabel",
        )
        disclaimer_label.pack(side=tb.BOTTOM, anchor="e", pady=10, padx=10)
