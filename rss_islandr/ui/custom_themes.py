import ttkbootstrap as tb

from rss_islandr.core.datatypes import UISettings


class CustomThemes:
    """
    Defining custom themes
    ----------------------
    Once defined they may be infered with their style alias directly anywhere in the code.

    The standard naming convention of a new syle is: CustomName.WidgetType

    WidgetType options:
        * TLabel (for ttk.Label)
        * TButton (for ttk.Button)
        * TCombobox (for ttk.Combobox)
        * TFrame (for ttk.Frame)
        * TNotebook (for ttk.Notebook)
        * TEntry (for ttk.Entry)
        * TCheckbutton (for ttk.Checkbutton)
        * TRadiobutton (for ttk.Radiobutton)
    """

    def __init__(self, style: tb.Style, ui_settings: UISettings):
        self.__style = style
        self.__ui_settings = ui_settings
        self.__str_to_color()

    def __str_to_color(self):
        """
        Conversion str to style.color. For example 'dark' will become style.color.dark
        and then will be assigned to the corresponding ui_setting.
        """
        try:
            self.__ui_bg_color_1 = getattr(self.__style.colors, self.__ui_settings.ui_bg_color_1)
            self.__ui_bg_color_2 = getattr(self.__style.colors, self.__ui_settings.ui_bg_color_2)
            self.__ui_font_color_1 = getattr(self.__style.colors, self.__ui_settings.ui_font_color_1)
            self.__ui_font_color_2 = getattr(self.__style.colors, self.__ui_settings.ui_font_color_2)
        except AttributeError:
            raise ValueError("Color not found in style.colors")

    def custom_notebook(self):
        """Custom styles for Notebook widgets"""
        self.__style.configure("Custom.TNotebook", background=self.__ui_bg_color_1, borderwidth=0.0)

        #: Style for inactive tabs
        self.__style.configure(
            "Custom.TNotebook.Tab", background=self.__ui_bg_color_2, foreground=self.__ui_font_color_2
        )
        #: Style for active tab
        self.__style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", self.__ui_bg_color_1)],
            foreground=[("selected", self.__ui_font_color_1)],
        )

    def custom_labels(self):
        """Custom styles for label widgets"""
        self.__style.configure(
            "Title.TLabel",
            background=self.__ui_bg_color_1,  # Background color
            foreground=self.__ui_font_color_1,  # Font color
            font=(self.__ui_settings.ui_title_font_type, self.__ui_settings.ui_title_font_size, "bold"),  # Font type
            relief="flat",
        )

        self.__style.configure(
            "General.TLabel",
            background=self.__ui_bg_color_1,
            foreground=self.__ui_font_color_1,
            font=(self.__ui_settings.ui_font_type, self.__ui_settings.ui_font_size, "bold"),  # Font type
        )

        self.__style.configure(
            "EntryWidget.TLabel",
            background=self.__ui_bg_color_1,
            foreground=self.__ui_font_color_1,
            font=(self.__ui_settings.ui_font_type, self.__ui_settings.ui_font_size, "bold"),  # Font type
            borderwidth=0,  # Border width
        )

    def custom_frame(self):
        self.__style.configure(
            "NavbarPad.TFrame",
            background=self.__ui_bg_color_1,
        )
        self.__style.configure(
            "Custom.TFrame",
            background=self.__ui_bg_color_1,
            foreground=self.__ui_font_color_1,
        )

    def custom_buttons(self):
        """Not USED"""
        background_color = self.__style.colors.get("bg")
        self.__style.configure(
            "Custom.Menubutton.TMenubutton",  # Custom style name
            background=background_color,  # Use the theme's background color
            foreground=self.__ui_font_color_1,  # Set the text color to white
            relief="flat",  # Remove the border (flat appearance)
            borderwidth=0,  # Set border width to 0
            padding=10,  # Add padding (optional)
        )
        self.__style.map(
            "Custom.Menubutton.TMenubutton",
            background=[("active", self.__ui_bg_color_2)],  # Change background color on hover
            foreground=[("active", self.__ui_font_color_2)],
        )

    def custom_combobox(self):
        """Not USED"""
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
            background=self.__ui_bg_color_2,  # Background color of the Combobox
            foreground=self.__ui_font_color_1,  # Text color
            fieldbackground=self.__ui_bg_color_1,  # Background color of the input field
            arrowcolor=self.__ui_bg_color_2,
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
        # self.custom_combobox()
        self.custom_buttons()
