import ttkbootstrap as tb
from rss_islandr.core.datatypes import UISettings
# TLabel (for ttk.Label)

# TButton (for ttk.Button)

# TCombobox (for ttk.Combobox)

# TFrame (for ttk.Frame)

# TNotebook (for ttk.Notebook)

# TEntry (for ttk.Entry)

# TCheckbutton (for ttk.Checkbutton)


# TRadiobutton (for ttk.Radiobutton)
class CustomThemes:
    """
    Defining custom themes
    ----------------------
    Once defined they may be infered with their style alias directly anywhere in the code.

    The standard convention is to use the format:

    CustomName.WidgetType
    """

    def __init__(self, theme: str, ui_settings: UISettings):
        self.__style = tb.Style(theme)
        self.ui_settings = ui_settings
        self.__str_to_color()

    def __str_to_color(self):
        """
        This will convert str to style.color. For example 'dark' will become style.color.dark
        and then will be assigned to the corresponding ui_setting.
        """
        try:
            self.ui_settings.ui_bg_color_1 = getattr(self.__style.colors, self.ui_settings.ui_bg_color_1)
            self.ui_settings.ui_bg_color_2 = getattr(self.__style.colors, self.ui_settings.ui_bg_color_2)
            self.ui_settings.ui_bg_color_3 = getattr(self.__style.colors, self.ui_settings.ui_bg_color_3)
            self.ui_settings.ui_font_color_1 = getattr(self.__style.colors, self.ui_settings.ui_font_color_1)
            self.ui_settings.ui_font_color_2 = getattr(self.__style.colors, self.ui_settings.ui_font_color_2)
            self.ui_settings.ui_font_color_3 = getattr(self.__style.colors, self.ui_settings.ui_font_color_3)
        except AttributeError:
            raise ValueError(f"Color '{self.ui_settings.ui_bg_color_2}' not found in style.colors")

    def custom_notebook(self):
        self.__style.configure("Custom.TNotebook", background=self.ui_settings.ui_bg_color_1, borderwidth=0.0)

        #: Style for inactive tabs
        self.__style.configure(
            "Custom.TNotebook.Tab",
            background=self.ui_settings.ui_bg_color_2,
            foreground=self.ui_settings.ui_font_color_2,
        )
        #: Style for active tab
        self.__style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", self.ui_settings.ui_bg_color_1)],
            foreground=[("selected", self.ui_settings.ui_font_color_1)],
        )

    def custom_labels(self):
        self.__style.configure(
            "Title.TLabel",
            background=self.ui_settings.ui_bg_color_1,  # Background color
            foreground=self.ui_settings.ui_font_color_1,  # Font color
            font=(self.ui_settings.ui_title_font_type, self.ui_settings.ui_title_font_size, "bold"),  # Font type
            relief="solid",
        )

        self.__style.configure(
            "General.TLabel",
            background=self.ui_settings.ui_bg_color_1,
            foreground=self.ui_settings.ui_font_color_1,
            font=(self.ui_settings.ui_font_type, self.ui_settings.ui_font_size, "bold"),  # Font type
        )

        self.__style.configure(
            "EntryWidget.TLabel",
            background=self.ui_settings.ui_bg_color_1,
            foreground=self.ui_settings.ui_font_color_1,
            font=(self.ui_settings.ui_font_type, self.ui_settings.ui_font_size, "bold"),  # Font type
            borderwidth=0,  # Border width
        )

    def custom_frame(self):
        self.__style.configure(
            "Custom.TFrame",
            background=self.ui_settings.ui_bg_color_1,
            foreground=self.ui_settings.ui_font_color_1,
        )

    def custom_combobox(self):
        self.__style.layout(
            "Custom.TCombobox",
            [
                (
                    "Combobox.button",  # Reintroduce the button element
                    {
                        "side": "right",  # Place the button on the right
                        "children": [
                            (
                                "Combobox.downarrow",  # Element name
                                {"sticky": "ns"},  # Properties
                            )
                        ],
                    },
                ),
                (
                    "Combobox.field",
                    {
                        "sticky": "nswe",  # Make the field stretch in all directions
                        "border": "0",  # Remove any border
                        "children": [
                            (
                                "Combobox.padding",
                                {
                                    "sticky": "nswe",  # Make padding stretch
                                    "children": [
                                        ("Combobox.textarea", {"sticky": "nswe"})  # Make text area stretch
                                    ],
                                },
                            )
                        ],
                    },
                ),
            ],
        )

        self.__style.configure(
            "Custom.TCombobox",
            background=self.ui_settings.ui_bg_color_2,  # Background color of the Combobox
            foreground=self.ui_settings.ui_font_color_1,  # Text color
            fieldbackground=self.ui_settings.ui_bg_color_1,  # Background color of the input field
            arrowcolor=self.ui_settings.ui_bg_color_3,
        )

    def __call__(self):
        """
        _summary_

        Parameters
        ----------
        theme : str
            Theme used in the main tb.Window()
        """
        self.custom_notebook()
        self.custom_labels()
        self.custom_frame()
        self.custom_combobox()
