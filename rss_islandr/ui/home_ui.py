import ttkbootstrap as tb
from core.config_parser import settings
from core.datatypes import UISettings
from core.skin_reader import read_skin_details
from custom_themes import CustomThemes


class HomeUI:
    def __init__(self, parent_frame: tb.Frame, ui_settings: UISettings, widgets_reconfigured: dict):
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
        self.__parent_frame = parent_frame
        self.__theme_type = "dark"
        self.ui_settings = ui_settings
        self.__widgets_reconfigured = widgets_reconfigured
        self.__home_nav_bar_frame = self.__create_horizontal_navbar()

    def frame_distances(self, frame) -> None:
        for i in range(1):
            frame.rowconfigure(i, weight=1)
        for i in range(11):
            frame.columnconfigure(i, weight=1)

    def __create_horizontal_navbar(self) -> tb.Frame:
        """Create a horizontal navbar for the home page"""
        nav_bar_frame = tb.Frame(self.__parent_frame)
        nav_bar_frame.place(relx=0, rely=0, relwidth=1.0, relheight=0.05)
        self.frame_distances(nav_bar_frame)

        return nav_bar_frame

    def toggle_theme(self):
        """Switch theme (dark-light)"""

        if self.__theme_type == "dark":  # If the current theme is dark, switch to light
            self.__theme_type = "light"
            self.toggle_button.config(text="Switch to Dark Mode")
            ui_settings_changed = read_skin_details(settings, self.__theme_type)
            theme_ttk = ui_settings_changed.ui_ttkbootstrap_theme
        else:  # If the current theme is light, switch to dark
            self.__theme_type = "dark"
            self.toggle_button.config(text="Switch to Light Mode")
            ui_settings_changed = read_skin_details(settings, self.__theme_type)
            theme_ttk = ui_settings_changed.ui_ttkbootstrap_theme

        self.__style = tb.Style(theme=theme_ttk)
        CustomThemes(self.__style, ui_settings_changed)()

        self.__reassign_values(ui_settings_changed)
        for widget, boot_style in self.__widgets_reconfigured.items():
            widget.configure(bootstyle=getattr(self.ui_settings, boot_style))

    def __reassign_values(self, ui_settings_changed: UISettings):
        """After changing skin values are reassigned"""
        for key, value in ui_settings_changed.__dict__.items():
            setattr(self.ui_settings, key, value)

    def __toggle_btn(self, frame: tb.Frame):
        self.toggle_button = tb.Checkbutton(
            frame,
            text="Switch to Light Mode",
            style="round-toggle",
            command=self.toggle_theme,
        )
        self.toggle_button.grid(row=0, column=10)

    def ui(self):
        self.__toggle_btn(self.__home_nav_bar_frame)
