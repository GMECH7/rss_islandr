from typing import Callable

import ttkbootstrap as tb
from general_ui import GeneralUITemplate

from rss_islandr.assessment import risk_calc, risk_color_assignment
from rss_islandr.core.config_parser import RECEPTOR_FACTORS_JSON_DIR, RISK_FACTORS_JSON_DIR
from rss_islandr.core.datatypes import FramePlacing, UICalcVariable, UIInpVariable, UISettings
from rss_islandr.core.exceptions import ExcelRowColNotFoundError
from rss_islandr.data_readers import ReceptorAliases, ReceptorFactorsFetcher, RisksDataFetcher


class AssessmentNoteBookUI(GeneralUITemplate):
    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        frame_geometry_dict: dict[str, FramePlacing],
        source_keys: list[str],
        pathway_keys: list[str],
        receptor_keys: list[str],
    ):
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.frame_geometry_dict = frame_geometry_dict

        self.hazard_fetcher = RisksDataFetcher(RISK_FACTORS_JSON_DIR)
        self.receptor_fetcher = ReceptorFactorsFetcher(RECEPTOR_FACTORS_JSON_DIR)
        self.receptor_aliases = ReceptorAliases(RECEPTOR_FACTORS_JSON_DIR)

        self.__receptor_alias_to_key_dict = {k: v for (v, k) in self.receptor_aliases.getter().items()}
        self.__receptor_key_to_alias = self.receptor_aliases.getter()

        self.__source_keys = source_keys
        self.__pathway_keys = pathway_keys
        self.__receptor_keys = receptor_keys
        self.__source_pathway_keys = self.__source_keys + self.__pathway_keys

        self.__init__risk_selection_dict()
        self.__init__receptor_risk_selection_dict()

        self.__init__source_pathway_dropdown()
        self.__init__receptor_dropdown()

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

    def __assemble_xlsx_row(self, i: int, parent_excel_col: str, parent_excel_row: int) -> tuple[str, str]:
        excel_cell = f"{parent_excel_col}{parent_excel_row + i}"
        excel_cell_risk = f"{parent_excel_col}{parent_excel_row + i + 1}"

        return excel_cell, excel_cell_risk

    def __init__source_pathway_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used in source and pathway calculations dropdown lists.
        """
        for risk_factor_key in self.__source_pathway_keys:
            mechanisms_dict = self.hazard_fetcher.getter(risk_factor_key)["mechanism"]
            parent_excel_col, parent_excel_row = self.__get_xlsx_row_col(risk_factor_key)

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
                self.__risk_selection[f"{risk_factor_key}_frame"].update(
                    {mechanism_alias: {"var": var, "weights": alias_to_weight}}
                )

                ui_var = UIInpVariable(
                    frame_tag=f"{risk_factor_key}_frame",
                    tk_var=var,
                    rel_pos=i,
                    text_val=mechanism_alias,
                    text_descr=None,
                    drop_options=dropdown_severity,
                    excel_cell=excel_cell,
                    state="enabled",
                )
                self.ui_inp_vars.update({f"drop_{risk_factor_key}_1_0{i}": ui_var})

            ui_calc_var = UICalcVariable(tb.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{risk_factor_key}_frame": ui_calc_var})
            self.frame_geometry_dict[f"{risk_factor_key}_frame"].n_row = i + 2

        return None

    def __init__risk_selection_dict(self):
        """
        This is a method used in the __init__.

        It initializes the risk_selection_dict with the following format:
        key: f'{<source or pathway_key>}'
        Value: empty dictionary which when populated is of type {<mechanism_alias>:RiskSelectionDict}.

        This dictionary is used to map severity aliases used in the dropdown lists to their weight value.
        """
        self.__risk_selection = {}
        for key in self.__source_pathway_keys:
            self.__risk_selection.update({f"{key}_frame": {}})

    def __init__receptor_risk_selection_dict(self):
        """
        This is a method used in the __init__.
        """
        self.__receptor_risk_selection = {}
        for key in self.__receptor_keys:
            self.__receptor_risk_selection.update({f"{key}_frame": {}})

    def __init__receptor_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used receptor calculations dropdown lists.
        """
        for key in self.__receptor_keys:
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
            self.__receptor_risk_selection[f"{key}_frame"].update(
                {
                    f"{key}_frame": {
                        "pathway": pathway_var,
                        "var": receptor_param,
                        "weights": param_alias_to_weight,
                    }
                }
            )

            ui_var_pathway = UIInpVariable(
                frame_tag=f"{key}_frame",
                tk_var=pathway_var,
                rel_pos=0,
                text_val="Pathway",
                text_descr=None,
                drop_options=dropdown_available_pathways_aliases,
                excel_cell=f"{parent_excel_col}{parent_excel_row}",
                state="enabled",
            )

            ui_var_receptor_param = UIInpVariable(
                frame_tag=f"{key}_frame",
                tk_var=receptor_param,
                rel_pos=1,
                text_val="Parameter",
                text_descr=None,
                drop_options=dropdown_receptor_param,
                excel_cell=f"{parent_excel_col}{parent_excel_row + 1}",
                state="enabled",
            )
            self.ui_inp_vars.update({f"drop_{key}_1_0": ui_var_pathway})
            self.ui_inp_vars.update({f"drop_{key}_1_1": ui_var_receptor_param})

            # always two rows in receptor dropdown
            excel_cell_risk = f"{parent_excel_col}{parent_excel_row + 2}"
            ui_calc_var = UICalcVariable(tb.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{key}_frame": ui_calc_var})
            self.frame_geometry_dict[f"{key}_frame"].n_row = 3

    def __create_new_tab(
        self, notebook: tb.Notebook, frame_tag: str, frame_title: str, calc_risk_command: Callable
    ) -> None:
        tab = tb.Frame(notebook)
        notebook.add(tab, text=frame_title)

        self.__create_new_risk_frame(tab, frame_tag, frame_title, calc_risk_command)

    def __calculate_source_pathway_risk(self, frame: tb.Frame, frame_tag: str):
        """
        Retrieves selected dropdown values and prints their corresponding weights.
        """
        weights = []
        for data in self.__risk_selection[frame_tag].values():
            selected_alias = data["var"].get()
            selected_weight = data["weights"].get(selected_alias, 0.0)
            weights.append(selected_weight)

        risk = risk_calc(weights)

        color = risk_color_assignment(risk)

        self.ui_calc_vars[frame_tag].tk_var.set(f"{risk}")
        self.__light_bulb(frame, frame_tag, color)

    def __calculate_receptor_total_risk(self, frame: tb.Frame, frame_tag: str) -> None:
        """ """
        data = self.__receptor_risk_selection[frame_tag][frame_tag]

        pathway_alias = data["pathway"].get()
        pathway_key = self.__receptor_alias_to_key_dict[pathway_alias]

        receptor_alias = data["var"].get()
        receptor_weight = data["weights"].get(receptor_alias, 0.0)

        source_risk = float(self.ui_calc_vars["IN_frame"].tk_var.get())
        pathway_risk = float(self.ui_calc_vars[f"{pathway_key}_frame"].tk_var.get())

        receptor_risk = risk_calc([source_risk, pathway_risk, receptor_weight])
        color = risk_color_assignment(receptor_risk)

        self.ui_calc_vars[frame_tag].tk_var.set(f"{receptor_risk}")
        self.__light_bulb(frame, frame_tag, color)

    def __create_new_risk_frame(self, frame, frame_tag: str, frame_title: str, calc_risk_command: Callable) -> tb.Frame:
        """ """
        frame_child = self.gt_new_frame(frame, frame_tag, frame_title)

        for dropdown_key in self.ui_inp_vars:
            if self.ui_inp_vars[dropdown_key].frame_tag == frame_tag:
                self.gt_combobox_widget(frame_child, dropdown_key)

        self.__btn_calculate_risk(frame_child, frame_tag, calc_risk_command)
        self.__light_bulb(frame_child, frame_tag, "white")

        # frame_child_2 = tb.Frame(frame)
        # frame_child_2 = tb.Frame(frame)
        # frame_child_2.place(relx=0.3, rely=0.5, relwidth=0.5, relheight=0.5)
        # self.risk_meter = tb.Progressbar(frame_child_2, orient="horizontal", length=200, mode="determinate")
        # self.risk_meter.pack(fill="y")  # Adjust padding as needed

        return frame

    def __btn_calculate_risk(self, frame: tb.Frame, frame_tag: str, calc_risk_command: Callable):
        calculate_btn = tb.Button(
            frame,
            text="Calculate risk",
            command=lambda: calc_risk_command(frame, frame_tag),
        )

        calculate_btn.grid(
            row=self.frame_geometry_dict[frame_tag].n_row - 1,
            rowspan=2,
            column=0,
            sticky="nsew",
        )

    def __light_bulb(self, frame: tb.Frame, frame_tag: str, color: str) -> None:
        """ """
        light = tb.Label(frame, text=f"{self.ui_calc_vars[frame_tag].tk_var.get()}")
        light.grid(
            row=self.frame_geometry_dict[frame_tag].n_row - 1,
            rowspan=2,
            column=1,
            sticky="nsew",
        )

    def __create_frame_tags_titles(self, case: str, keys: list[str]):
        frame_tags_titles = []
        if case == "source" or case == "pathway":
            for risk_factor_key in keys:
                frame_tag = f"{risk_factor_key}_frame"
                frame_title = f"{self.hazard_fetcher.getter(risk_factor_key)['alias']}"
                frame_tags_titles.append((frame_tag, frame_title))
        else:
            for risk_factor_key in keys:
                frame_tag = f"{risk_factor_key}_frame"
                frame_title = f"{self.__receptor_key_to_alias[risk_factor_key[:2]]}"
                frame_tags_titles.append((frame_tag, frame_title))
        return frame_tags_titles

    def ui(self, parent_frame: tb.Frame, case: str):
        if case == "source":
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__source_keys)
            calc_risk_command = self.__calculate_source_pathway_risk
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        elif case == "pathways":
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__pathway_keys)
            calc_risk_command = self.__calculate_source_pathway_risk
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        elif case == "receptors":
            frame_tags_titles = self.__create_frame_tags_titles(case, self.__receptor_keys)
            calc_risk_command = self.__calculate_receptor_total_risk
            notebook = tb.Notebook(parent_frame, style="Custom.TNotebook")
            notebook.pack(fill="both", expand=True)

        for frame_tag, frame_title in frame_tags_titles:
            self.__create_new_tab(notebook, frame_tag, frame_title, calc_risk_command)
