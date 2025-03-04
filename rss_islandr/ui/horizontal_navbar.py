import ttkbootstrap as tb
from general_ui import frame_distances

from rss_islandr.ui.horizontal_navbar_btns import HorizontalNavbarBtns


class HorizontalNavbar:
    """Horizontal navbar definition."""

    def __init__(
        self,
        ui_settings,
        ui_inp_vars,
        ui_calc_vars,
        widgets_reconfigured: dict[tb.Frame, str],
        rel_height: float = 0.05,
        rel_width: float = 1.0,
    ):
        self.__rel_height = rel_height
        self.__rel_width = rel_width
        self.__horizontal_navbar = HorizontalNavbarBtns(ui_settings, ui_inp_vars, ui_calc_vars, widgets_reconfigured)

    def __create_horizontal_navbar(self, parent_frame: tb.Frame) -> tb.Frame:
        """Create a horizontal navbar."""
        nav_bar_frame = tb.Frame(parent_frame)
        nav_bar_frame.place(relx=0, rely=0, relwidth=self.__rel_width, relheight=self.__rel_height)
        frame_distances(nav_bar_frame, 1, 12)
        self.__horizontal_navbar.file_menu_btn(nav_bar_frame)
        self.__horizontal_navbar.docs_menu_button(nav_bar_frame)
        self.__horizontal_navbar.toggle_skin_btn(nav_bar_frame)

        return nav_bar_frame

    def __create_child_frame(self, parent_frame: tb.Frame) -> tb.Frame:
        """Create a child frame (under the horizontal navbar)."""
        child_frame = tb.Frame(parent_frame)
        child_frame.place(relx=0, rely=self.__rel_height, relwidth=self.__rel_width, relheight=1 - self.__rel_height)

        return child_frame

    def __call__(self, parent_frame: tb.Frame):
        """ """
        navbar_frame = self.__create_horizontal_navbar(parent_frame)
        child_frame = self.__create_child_frame(parent_frame)

        return navbar_frame, child_frame
