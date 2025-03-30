import ttkbootstrap as tb

from rss_islandr.ui.assessment_notebook_ui import AssessmentNoteBookUI
from rss_islandr.ui.horizontal_navbar import HorizontalNavbar


class AppUI:
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
        self.__navbar_width = 0.1
        self.__navbar_padx = 0.005
        self.__frames_xstart = self.__navbar_width + self.__navbar_padx
        self.__frames_width = 1.0 - self.__navbar_padx - self.__navbar_width

        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.meter_frames = meter_frames
        self.frame_geometry_dict = frame_geometry_dict
        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = receptor_keys
        self.widgets_reconfigured = widgets_reconfigured

    def ui(self, root):
        """No functionality is added in the main page."""

        self.__source_page_1 = tb.Frame(root)
        self.__pathways_page_1 = tb.Frame(root)
        self.__receptors_page_1 = tb.Frame(root)

        # self.__source_page_2 = tb.Frame(root)
        # self.__pathways_page_2 = tb.Frame(root)
        # self.__receptors_page_2 = tb.Frame(root)

        self.__create_source_btn(self.__parent_navbar_frame, self.__source_page_1)
        self.__create_pathways_btn(self.__parent_navbar_frame, self.__pathways_page_1)
        self.__create_receptors_btn(self.__parent_navbar_frame, self.__receptors_page_1)

        # self.__create_source_btn(self.__parent_navbar_frame, self.__source_page_2)
        # self.__create_pathways_btn(self.__parent_navbar_frame, self.__pathways_page_2)
        # self.__create_receptors_btn(self.__parent_navbar_frame, self.__receptors_page_2)

        app_assesment_1 = AssessmentNoteBookUI(
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

        app_assesment_2 = AssessmentNoteBookUI(
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

        for self.page in [
            self.__source_page_1,
            self.__pathways_page_1,
            self.__receptors_page_1,
            # self.__source_page_2,
            # self.__pathways_page_2,
            # self.__receptors_page_2,
        ]:
            self.page.place(
                relx=self.__frames_xstart,
                rely=0,
                relwidth=self.__frames_width,
                relheight=1.0,
            )
        source_navbar_frame, source_frame = HorizontalNavbar(
            self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        )(self.__source_page_1)

        pathways_navbar_frame, pathways_frame = HorizontalNavbar(
            self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        )(self.__pathways_page_1)

        receptors_navbar_frame, receptors_frame = HorizontalNavbar(
            self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        )(self.__receptors_page_1)

        app_assesment_1.ui(source_navbar_frame, source_frame, "source")
        app_assesment_1.ui(pathways_navbar_frame, pathways_frame, "pathways")
        app_assesment_1.ui(receptors_navbar_frame, receptors_frame, "receptors")

        # source_navbar_frame, source_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__source_page_1)

        # pathways_navbar_frame, pathways_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__pathways_page_1)

        # receptors_navbar_frame, receptors_frame = HorizontalNavbar(
        #     self.ui_settings, self.ui_inp_vars, self.ui_calc_vars, self.widgets_reconfigured
        # )(self.__receptors_page_1)

        # app_assesment_2.ui(source_navbar_frame, source_frame, "source")
        # app_assesment_2.ui(pathways_navbar_frame, pathways_frame, "pathways")
        # app_assesment_2.ui(receptors_navbar_frame, receptors_frame, "receptors")

    def __create_source_btn(self, nav_bar_frame: tb.Frame, page) -> None:
        """ """
        btn_source = tb.Button(
            nav_bar_frame,
            text="Source",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(page),
        )
        btn_source.grid(row=0, column=2, sticky="nsew")
        self.widgets_reconfigured[btn_source] = "ui_btn_bg_color_1"

    def __create_pathways_btn(self, nav_bar_frame: tb.Frame, page) -> None:
        """ """
        btn_pathways = tb.Button(
            nav_bar_frame,
            text="Pathways",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(page),
        )
        btn_pathways.grid(row=0, column=3, sticky="nsew")
        self.widgets_reconfigured[btn_pathways] = "ui_btn_bg_color_1"

    def __create_receptors_btn(self, nav_bar_frame: tb.Frame, page) -> None:
        """ """
        btn_receptors = tb.Button(
            nav_bar_frame,
            text="Receptors",
            style=self.ui_settings.ui_btn_bg_color_1,
            command=lambda: self.__show_page(page),
        )
        btn_receptors.grid(row=0, column=4, sticky="nsew")
        self.widgets_reconfigured[btn_receptors] = "ui_btn_bg_color_1"

    def __show_page(self, page):
        page.tkraise()
