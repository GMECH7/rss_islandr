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
        """
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame

    def ui(self):
        """No functionality is added in the main page."""
        pass
