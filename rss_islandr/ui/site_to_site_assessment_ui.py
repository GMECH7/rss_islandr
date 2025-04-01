import ttkbootstrap as tb

from rss_islandr.ui.assessment_notebook_ui import AssessmentNoteBookUI
from rss_islandr.ui.btns_change_colour import BtnsChangeColour
from rss_islandr.ui.general_ui import frame_distances


class SiteToSiteAssessmentUI:
    """
    Implementation of UI for visualizing a site to site assessment
    1. On-site to on-site
    2. On-site to off-site
    3. Off-site to on-site
    """

    def __init__(
        self,
        parent_navbar_frame: tb.Frame,
        parent_frame: tb.Frame,
        ui_settings,
        ui_inp_vars,
        ui_calc_vars,
        meter_frames,
        frame_geometry_dict,
        source_keys,
        pathway_keys,
        receptor_keys,
        widgets_reconfigured,
    ):
        self.__parent_navbar_frame = parent_navbar_frame
        self.__parent_frame = parent_frame

        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.meter_frames = meter_frames
        self.frame_geometry_dict = frame_geometry_dict
        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = receptor_keys
        self.widgets_reconfigured = widgets_reconfigured
        # Store references to navigation buttons - used for restyling buttons when pressed
        self.__nav_buttons_references = {}
        self.__init__handle_geometry()

    def __init__handle_geometry(self):
        """ """
        self.__navbar_width = 0.1
        self.__navbar_padx = 0.005
        self.__frames_xstart = self.__navbar_width + self.__navbar_padx
        self.__frames_width = 1.0 - self.__navbar_padx - self.__navbar_width
        self.__frame_n_rows = self.frame_geometry_dict["vertical_navbar_assessment_frames"].n_row
        self.__frame_n_cols = self.frame_geometry_dict["vertical_navbar_assessment_frames"].n_col

    def __create_source_btn(self, nav_bar_frame: tb.Frame, page) -> tb.Button:
        """ """
        btn_source = tb.Button(
            nav_bar_frame,
            text="Source",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(page, "source"),
        )
        btn_source.grid(row=0, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_source] = "ui_btn_bg_color_1"
        return btn_source

    def __create_pathways_btn(self, nav_bar_frame: tb.Frame, page) -> tb.Button:
        """ """
        btn_pathways = tb.Button(
            nav_bar_frame,
            text="Pathways",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(page, "pathways"),
        )
        btn_pathways.grid(row=1, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_pathways] = "ui_btn_bg_color_1"
        return btn_pathways

    def __create_receptors_btn(self, nav_bar_frame: tb.Frame, page_frame: tb.Frame) -> tb.Button:
        """ """
        btn_receptors = tb.Button(
            nav_bar_frame,
            text="Receptors",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__btns_cc.show_page(page_frame, "receptors"),
        )
        btn_receptors.grid(row=2, column=0, sticky="nsew")
        self.widgets_reconfigured[btn_receptors] = "ui_btn_bg_color_1"
        return btn_receptors

    def __create_vertical_navbar(self, root) -> tb.Frame:
        """Create vertical navbar visible in all app."""
        nav_bar_frame = tb.Frame(root)
        nav_bar_frame.place(relx=0, rely=0, relwidth=self.__navbar_width, relheight=1.0)
        frame_distances(nav_bar_frame, self.__frame_n_rows, self.__frame_n_cols)
        nav_bar_pad_frame = tb.Frame(root, style="NavbarPad.TFrame")
        nav_bar_pad_frame.place(relx=self.__navbar_width, rely=0, relwidth=self.__navbar_padx, relheight=1.0)
        return nav_bar_frame

    def __create_vertical_navbar_buttons(self, root, pages: list[tb.Frame]) -> None:
        """
        Create vertical navbar buttons
        """
        nav_bar_frame = self.__create_vertical_navbar(root)
        self.__nav_buttons_references["source"] = self.__create_source_btn(nav_bar_frame, pages[0])
        self.__nav_buttons_references["pathways"] = self.__create_pathways_btn(nav_bar_frame, pages[1])
        self.__nav_buttons_references["receptors"] = self.__create_receptors_btn(nav_bar_frame, pages[2])

    def ui(self, scenario_id: int):
        """ """
        self.__source_frame = tb.Frame(self.__parent_frame)
        self.__pathways_frame = tb.Frame(self.__parent_frame)
        self.__receptors_frame = tb.Frame(self.__parent_frame)
        self.__create_vertical_navbar_buttons(
            self.__parent_frame, [self.__source_frame, self.__pathways_frame, self.__receptors_frame]
        )
        self.__btns_cc = BtnsChangeColour(self.ui_settings, self.__nav_buttons_references)

        app_assesment = AssessmentNoteBookUI(
            scenario_id,
            self.ui_settings,
            self.ui_inp_vars,
            self.ui_calc_vars,
            self.meter_frames,
            self.frame_geometry_dict,
            self.__source_keys,
            self.__pathway_keys,
            self.__receptor_keys,
            widgets_reconfigured=self.widgets_reconfigured,
        )

        for self.page in [self.__source_frame, self.__pathways_frame, self.__receptors_frame]:
            self.page.place(
                relx=self.__frames_xstart,
                rely=0,
                relwidth=self.__frames_width,
                relheight=1.0,
            )

        app_assesment.ui(self.__source_frame, "source")
        app_assesment.ui(self.__pathways_frame, "pathways")
        app_assesment.ui(self.__receptors_frame, "receptors")
