import logging
from typing import Union

import ttkbootstrap as tb
from general_ui import GeneralUITemplate
from PIL import Image

from rss_islandr.assessment import risk_calc, risk_color_assignment
from rss_islandr.core.config_parser import RECEPTOR_FACTORS_JSON_DIR, RISK_FACTORS_JSON_DIR
from rss_islandr.core.datatypes import FramePlacing, UICalcVariable, UIInpVariable, UISettings
from rss_islandr.core.exceptions import ExcelRowColNotFoundError
from rss_islandr.data_readers import ReceptorAliases, ReceptorFactorsFetcher, RisksDataFetcher

Image.CUBIC = Image.BICUBIC


class AssessmentNoteBookUI(GeneralUITemplate):
    """
    This class creates a notebook with tabs for the contamination assessment.
    Each tab contains a frame with a dropdown list and a meter widget.
    """

    def __init__(
        self,
        scenario_id: str,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        meter_frames: dict[str, tb.Meter],
        frame_geometry_dict: dict[str, FramePlacing],
        source_keys: list[str],
        pathway_keys: list[str],
        receptor_keys: list[str],
        **kwargs,
    ):
        """
        Parameters
        ----------
        scenario_id : str
            The scenario id is used to identify the scenario in the UI.
            Options are "on-on", "on-off", "off-on".
        ui_settings : UISettings
            This is a dataclass that holds the ui settings.
            It is always initialized using the dark theme option,
            but gets updated when the toggle button is pressed.
        ui_inp_vars : dict[str, UIInpVariable]
            Dictionary that maps the input variables aliases to UI input variables.
        ui_calc_vars : dict[str, UICalcVariable]
            Dictionary that maps the calculated variables aliases to UI calculated variables.
        meter_frames : dict[str, tb.Meter]
            Dictionary that maps the frame tags to meter frames.
        frame_geometry_dict : dict[str, FramePlacing]
            Dictionary that maps the frame tags to their geometry as
            defined in the settings.json file.
        source_keys : list[str]
            Source keys eg. 'IN'.
        pathway_keys : list[str]
            Pathway keys eg. 'SW'.
        receptor_keys : list[str]
            Receptor keys eg. 'SW_receptor'
        """
        self.scenario_id = scenario_id
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.meter_frames = meter_frames
        self.frame_geometry_dict = frame_geometry_dict
        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = receptor_keys
        self.__source_pathway_keys = self.__source_keys + self.__pathway_keys
        self.__widgets_reconfigured = kwargs.get("widgets_reconfigured", {})

        self.hazard_fetcher = RisksDataFetcher(RISK_FACTORS_JSON_DIR)
        self.receptor_fetcher = ReceptorFactorsFetcher(RECEPTOR_FACTORS_JSON_DIR)
        self.receptor_aliases = ReceptorAliases(RECEPTOR_FACTORS_JSON_DIR)

        self.__receptor_alias_to_key_dict = {k: v for (v, k) in self.receptor_aliases.getter().items()}
        self.__receptor_key_to_alias = self.receptor_aliases.getter()

        self.__init__risk_selection_dict()
        self.__init__receptor_risk_selection_dict()
        self.__init__source_pathway_dropdown()
        self.__init__receptor_dropdown()
        self.__init__create_traces_receptors()

        super().__init__(ui_settings, ui_inp_vars, self.frame_geometry_dict)

    def __get_xlsx_row_col(self, risk_factor_key: str) -> tuple[str, int]:
        """
        Get excel column and row for the source and pathways.

        Parameters
        ----------
        risk_factor_key : str
            Risk factor key. eg. 'IN', 'SW', etc.

        Returns
        -------
        tuple[str, float]
            _description_
        """
        try:
            parent_excel_col = self.hazard_fetcher.getter(risk_factor_key)["excel_col"]
            parent_excel_row = self.hazard_fetcher.getter(risk_factor_key)["excel_row"]
        except Exception:
            raise ExcelRowColNotFoundError

        return parent_excel_col, parent_excel_row

    def __get_pdf_table_name(self, data_fetcher, risk_factor_key) -> Union[str, None]:
        try:
            pdf_table_name = data_fetcher.getter(risk_factor_key)["pdf_table_name"]
        except Exception:
            pdf_table_name = None

        return pdf_table_name

    def __assemble_xlsx_row(self, i: int, parent_excel_col: str, parent_excel_row: int) -> tuple[str, str]:
        """ """
        excel_cell = f"{parent_excel_col}{parent_excel_row + i}"
        # TODO I have altered the dynamic calculation. I must see how to do that in the future
        # excel_cell_risk = f"{parent_excel_col}{parent_excel_row + i + 1}"
        excel_cell_risk = f"{parent_excel_col}9" if parent_excel_row == 7 else f"{parent_excel_col}17"

        return excel_cell, excel_cell_risk

    def __init__source_pathway_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used in source and pathway calculations dropdown lists.
        """
        for risk_factor_key in self.__source_pathway_keys:
            mechanisms_dict = self.hazard_fetcher.getter(risk_factor_key)["mechanism"]
            parent_excel_col, parent_excel_row = self.__get_xlsx_row_col(risk_factor_key)
            pdf_table_name = self.__get_pdf_table_name(self.hazard_fetcher, risk_factor_key)

            for i, mechanism_key in enumerate(mechanisms_dict):
                mechanism_alias = self.hazard_fetcher.getter(risk_factor_key, mechanism_key)["alias"]
                severity_dict = self.hazard_fetcher.getter(risk_factor_key, mechanism_key)["severity"]

                excel_cell, excel_cell_risk = self.__assemble_xlsx_row(i, parent_excel_col, parent_excel_row)

                dropdown_severity = []
                alias_to_weight = {}

                for severity_key in severity_dict:
                    severity_alias = severity_dict[severity_key]["alias"]
                    severity_weight = severity_dict[severity_key]["weight"]
                    dropdown_severity.append(severity_alias)
                    alias_to_weight[severity_alias] = severity_weight

                var = tb.StringVar()
                var.set(dropdown_severity[0])

                # Store weight mapping for later use
                self.__risk_selection[f"{risk_factor_key}_{self.scenario_id}_frame"].update(
                    {mechanism_alias: {"var": var, "weights": alias_to_weight}}
                )

                ui_var = UIInpVariable(
                    frame_tag=f"{risk_factor_key}_{self.scenario_id}_frame",
                    tk_var=var,
                    rel_pos=i,
                    text_val=mechanism_alias,
                    val_default=dropdown_severity[0],
                    text_descr=None,
                    drop_options=dropdown_severity,
                    excel_cell=excel_cell,
                    pdf_table_name=pdf_table_name,
                    state="enabled",
                )
                self.ui_inp_vars.update({f"drop_{self.scenario_id}_{risk_factor_key}_1_0{i}": ui_var})
                self.ui_inp_vars[f"drop_{self.scenario_id}_{risk_factor_key}_1_0{i}"].tk_var.trace_add(
                    "write",
                    lambda *args, rfk=risk_factor_key, idx=i: self.__calculate_source_pathway_risk(
                        f"{rfk}_{self.scenario_id}_frame"
                    ),
                )

            ui_calc_var = UICalcVariable(tb.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{risk_factor_key}_{self.scenario_id}_frame": ui_calc_var})
            self.frame_geometry_dict[f"{risk_factor_key}_{self.scenario_id}_frame"].n_row = i + 2

    def __init__risk_selection_dict(self) -> None:
        """
        This is a method used in the __init__.

        It initializes the risk_selection_dict with the following format:
        key: f'{<source or pathway_key>}'
        Value: empty dictionary which when populated is of type {<mechanism_alias>:RiskSelectionDict}.

        This dictionary is used to map severity aliases used in the dropdown lists to their weight value.
        """
        self.__risk_selection = {}
        for key in self.__source_pathway_keys:
            self.__risk_selection.update({f"{key}_{self.scenario_id}_frame": {}})

    def __init__receptor_risk_selection_dict(self):
        """
        This is a method used in the __init__.
        """
        self.__receptor_risk_selection = {}
        for key in self.__receptor_keys:
            self.__receptor_risk_selection.update({f"{key}_{self.scenario_id}_frame": {}})

    def __init__receptor_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used receptor calculations dropdown lists.
        """
        for key in self.__receptor_keys:
            pdf_table_name = self.__get_pdf_table_name(self.receptor_fetcher, key)
            try:
                parent_excel_col = self.receptor_fetcher.getter(key)["excel_col"]
                parent_excel_row = self.receptor_fetcher.getter(key)["excel_row"]
            except Exception:
                parent_excel_col = None

            dropdown_receptor_param = []
            param_alias_to_weight = {}

            parameters_dict = self.receptor_fetcher.getter(key)["parameter"]
            for parameter_key in parameters_dict:
                parameter_alias = self.receptor_fetcher.getter(key, parameter_key)["alias"]
                parameter_weight = self.receptor_fetcher.getter(key, parameter_key)["weight"]
                param_alias_to_weight[parameter_alias] = parameter_weight
                dropdown_receptor_param.append(parameter_alias)

            dropdown_available_pathways_keys = self.receptor_fetcher.getter(key)["available_pathways"]
            dropdown_available_pathways_aliases = [
                self.receptor_aliases.getter()[key] for key in dropdown_available_pathways_keys
            ]
            pathway_var = tb.StringVar()
            pathway_var.set(dropdown_available_pathways_aliases[0])

            receptor_param = tb.StringVar()
            receptor_param.set(dropdown_receptor_param[0])

            # Store weight mapping for later use
            self.__receptor_risk_selection[f"{key}_{self.scenario_id}_frame"].update(
                {
                    f"{key}_{self.scenario_id}_frame": {
                        "pathway": pathway_var,
                        "var": receptor_param,
                        "weights": param_alias_to_weight,
                    }
                }
            )

            ui_var_pathway = UIInpVariable(
                frame_tag=f"{key}_{self.scenario_id}_frame",
                tk_var=pathway_var,
                rel_pos=0,
                text_val="Pathway",
                val_default=dropdown_available_pathways_aliases[0],
                text_descr=None,
                drop_options=dropdown_available_pathways_aliases,
                excel_cell=f"{parent_excel_col}{parent_excel_row}",
                pdf_table_name=pdf_table_name,
                state="enabled",
            )

            ui_var_receptor_param = UIInpVariable(
                frame_tag=f"{key}_{self.scenario_id}_frame",
                tk_var=receptor_param,
                rel_pos=1,
                text_val="Parameter",
                val_default=dropdown_receptor_param[0],
                text_descr=None,
                drop_options=dropdown_receptor_param,
                excel_cell=f"{parent_excel_col}{parent_excel_row + 1}",
                pdf_table_name=pdf_table_name,
                state="enabled",
            )
            self.ui_inp_vars.update({f"drop_{key}_{self.scenario_id}_1_0": ui_var_pathway})
            self.ui_inp_vars.update({f"drop_{key}_{self.scenario_id}_1_1": ui_var_receptor_param})
            self.ui_inp_vars[f"drop_{key}_{self.scenario_id}_1_0"].tk_var.trace_add(
                "write",
                lambda *args, rfk=key: self.__calculate_receptor_total_risk(f"{rfk}_{self.scenario_id}_frame"),
            )
            self.ui_inp_vars[f"drop_{key}_{self.scenario_id}_1_1"].tk_var.trace_add(
                "write",
                lambda *args, rfk=key: self.__calculate_receptor_total_risk(f"{rfk}_{self.scenario_id}_frame"),
            )

            # always two rows in receptor dropdown
            excel_cell_risk = f"{parent_excel_col}{parent_excel_row + 2}"
            ui_calc_var = UICalcVariable(tb.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{key}_{self.scenario_id}_frame": ui_calc_var})

            self.frame_geometry_dict[f"{key}_{self.scenario_id}_frame"].n_row = 3

    def __init__create_traces_receptors(self) -> None:
        """
        Define traces for receptors' total risk.

        Receptors are dependent on sources and pathways.
        """
        for receptor_key in self.__receptor_keys:
            #: Available pathways per receptor
            available_pathways = self.receptor_fetcher.getter(receptor_key)["available_pathways"]
            for pathway in self.__source_keys + available_pathways:
                self.ui_calc_vars[f"{pathway}_{self.scenario_id}_frame"].tk_var.trace_add(
                    "write",
                    lambda *args, ptk=receptor_key: self.__calculate_receptor_total_risk(
                        f"{ptk}_{self.scenario_id}_frame"
                    ),
                )

    def __create_new_tab(self, notebook: tb.Notebook, frame_tag: str, frame_title: str, meter_widget_text: str) -> None:
        """ """
        tab = tb.Frame(notebook)
        notebook.add(tab, text=frame_title)
        self.__create_new_risk_frame(tab, frame_tag, frame_title, meter_widget_text)

    def __calculate_source_pathway_risk(self, frame_tag: str) -> None:
        """
        Retrieves selected dropdown values and prints their corresponding weights.
        """
        weights = []
        for data in self.__risk_selection[frame_tag].values():
            selected_alias = data["var"].get()
            selected_weight = data["weights"].get(selected_alias, "0")
            weights.append(selected_weight)

        risk = risk_calc(weights)
        self.ui_calc_vars[frame_tag].tk_var.set(f"{risk}")
        self.__update_meter(frame_tag)

    def __calculate_receptor_total_risk(self, frame_tag: str) -> None:
        """
        Calculate the total risk of the receptor.
        For this the respective source and the pathway risks should have been precalcualted.
        """
        data = self.__receptor_risk_selection[frame_tag][frame_tag]

        pathway_alias = data["pathway"].get()
        pathway_key = self.__receptor_alias_to_key_dict[pathway_alias]

        receptor_alias = data["var"].get()
        receptor_weight = data["weights"].get(receptor_alias, 0.0)

        source_risk = float(self.ui_calc_vars[f"IN_{self.scenario_id}_frame"].tk_var.get())
        pathway_risk = float(self.ui_calc_vars[f"{pathway_key}_{self.scenario_id}_frame"].tk_var.get())

        receptor_risk = risk_calc([source_risk, pathway_risk, receptor_weight])

        self.ui_calc_vars[frame_tag].tk_var.set(f"{receptor_risk}")

        self.__update_meter(frame_tag)

    def __update_meter(self, frame_tag: str) -> None:
        """Update meter on button click"""
        risk = float(self.ui_calc_vars[frame_tag].tk_var.get())
        color_ttk = risk_color_assignment(risk)

        if risk == 0.0:
            risk_formatted = "{:.0f}".format(risk)
            boot_style = "default"
        else:
            risk_formatted = "{:.1f}".format(100 * risk)
            boot_style = color_ttk
        self.meter_frames[f"{frame_tag}_risk"].configure(amountused=risk_formatted, bootstyle=boot_style)

    def __create_new_risk_frame(self, frame, frame_tag: str, frame_title: str, meter_widget_text: str) -> tb.Frame:
        """ """
        #: Create frame that will hold the entries, dropdowns etc.
        frame_form = self.gt_new_frame(frame, frame_tag, frame_title)
        #: Create frame that will hold risk meter
        frame_risk_meter = self.gt_new_frame_wo(frame, f"{frame_tag}_risk")

        for dropdown_key in self.ui_inp_vars:
            if self.ui_inp_vars[dropdown_key].frame_tag == frame_tag:
                self.gt_combobox_widget(frame_form, dropdown_key)

        meter = self.gt_meter_widget(frame_risk_meter, meter_widget_text)
        self.meter_frames[f"{frame_tag}_risk"] = meter

        return frame

    def __create_frame_tags_titles(self, case: str, keys: list[str]) -> list[tuple[str, str, str]]:
        """ """
        frame_tags_titles = []
        if case == "source" or case == "pathways":
            for risk_factor_key in keys:
                frame_tag = f"{risk_factor_key}_{self.scenario_id}_frame"
                frame_title = f"{self.hazard_fetcher.getter(risk_factor_key)['alias']}"
                meter_widget_text = "Hazard potential" if case == "source" else "Pathway risk"
                frame_tags_titles.append((frame_tag, frame_title, meter_widget_text))
        else:
            for risk_factor_key in keys:
                frame_tag = f"{risk_factor_key}_{self.scenario_id}_frame"
                frame_title = f"{self.__receptor_key_to_alias[risk_factor_key[:2]]}"
                meter_widget_text = "Risk"
                frame_tags_titles.append((frame_tag, frame_title, meter_widget_text))
        return frame_tags_titles

    def ui(self, parent_frame: tb.Frame, case: str) -> None:
        """ """
        if case == "source":
            logging.info(f"Creating {case} notebook for scenario {self.scenario_id}")
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__source_keys)
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        elif case == "pathways":
            logging.info(f"Creating {case} notebook for scenario {self.scenario_id}")
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__pathway_keys)
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        elif case == "receptors":
            logging.info(f"Creating {case} notebook for scenario {self.scenario_id}")
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__receptor_keys)
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        for frame_tag, frame_title, meter_widget_text in frame_tags_titles:
            self.__create_new_tab(notebook, frame_tag, frame_title, meter_widget_text)
