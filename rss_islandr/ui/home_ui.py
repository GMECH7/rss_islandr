import ttkbootstrap as tb
from core.datatypes import UISettings
from general_btns_ui import GeneralBtnsUI


class HomeUI:
    def __init__(
        self,
        parent_navbar_frame: tb.Frame,
        parent_frame: tb.Frame,
        ui_settings: UISettings,
        ui_inp_vars,
        ui_calc_vars,
        widgets_reconfigured: dict,
    ):
        """
        Home page

        Parameters
        ----------
        parent_frame : tb.Frame
            Parent frame.
        ui_settings : UISettings
            This is a dataclass that holds the ui settings.
            It is always initialized using the dark theme option,
            but gets updated when the toggle button is pressed.
        widgets_reconfigured : dict[tb.Frame, str]
            This dictionary holds the pair of frame and the bootsyle
            used in their rendering. All widgets that have a bootsyle
            which is not defined in the CustomThemes have to be included
            here in order to be restyled when the theme changes.
        """
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame
        self.gnrl_btns_ui = GeneralBtnsUI(ui_settings, ui_inp_vars, ui_calc_vars, widgets_reconfigured)

    def ui(self):
        self.gnrl_btns_ui.toggle_skin_btn(self.__parent_navbar_frame)
        self.gnrl_btns_ui.file_menu_btn(self.__parent_navbar_frame)
