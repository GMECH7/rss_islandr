import tkinter as tk
from tkinter import ttk

from general_ui import GeneralUITemplate

from rss_islandr.assessment import risk_calc, risk_color_assignment
from rss_islandr.core.config_parser import RECEPTOR_FACTORS_JSON_DIR, RISK_FACTORS_JSON_DIR
from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable, UISettings
from rss_islandr.data_readers import ReceptorAliases, ReceptorFactorsFetcher, RisksDataFetcher


class AssessmentNoteBookUI(GeneralUITemplate):

    def __init__(
        self,
        ui_settings: UISettings,
        ui_inp_vars: dict[str, UIInpVariable],
        ui_calc_vars: dict[str, UICalcVariable],
        root: tk.Toplevel,
        canvas_specs: list,
        frame_info_dict,
    ):
        self.ui_settings = ui_settings
        self.ui_inp_vars = ui_inp_vars
        self.ui_calc_vars = ui_calc_vars
        self.root = root
        self.frame_info_dict = frame_info_dict
        self.canvas_height = canvas_specs[0]
        self.canvas_width = canvas_specs[1]
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        super().__init__(
            ui_settings,
            ui_inp_vars,
            self.root,
            self.frame_info_dict["2"],
            self.canvas_height,
            self.canvas_width,
        )
        self.hazard_fetcher = RisksDataFetcher(RISK_FACTORS_JSON_DIR)
        self.receptor_fetcher = ReceptorFactorsFetcher(RECEPTOR_FACTORS_JSON_DIR)
        self.receptor_aliases = ReceptorAliases(RECEPTOR_FACTORS_JSON_DIR)

        self.__receptor_alias_to_key_dict = {
            k: v for (v, k) in self.receptor_aliases.getter().items()
        }
        self.__receptor_key_to_alias = self.receptor_aliases.getter()

        self.__source_keys = ["IN"]
        self.__pathway_keys = []  # ["SL", "GW", "SW", "AR", "SD"]
        self.__receptor_keys = [f"{pathway}_receptor" for pathway in self.__pathway_keys]
        self.__source_pathway_keys = self.__source_keys + self.__pathway_keys
        self.__source_pathway_receptor_keys = self.__source_pathway_keys + self.__receptor_keys

        self.__init__risk_selection_dict()
        self.__init__receptor_risk_selection_dict()

        super().__init__(
            ui_settings,
            ui_inp_vars,
            self.root,
            self.frame_info_dict["1"],
            self.canvas_height,
            self.canvas_width,
        )

        self.__init__source_pathway_dropdown()

    def __init__source_pathway_dropdown(self) -> None:
        """
        This is a method used in the __init__.

        This method defines the dropdown variables used in source and pathway calculations dropdown lists.
        """
        for key in self.__source_pathway_keys:
            mechanisms_dict = self.hazard_fetcher.getter(key)["mechanism"]

            try:
                parent_excel_col = self.hazard_fetcher.getter(key)["excel_col"]
                parent_excel_row = self.hazard_fetcher.getter(key)["excel_row"]
            except Exception:
                parent_excel_col = None

            for i, mechanism_key in enumerate(mechanisms_dict):
                mechanism_alias = self.hazard_fetcher.getter(key, mechanism_key)["alias"]
                severity_dict = self.hazard_fetcher.getter(key, mechanism_key)["severity"]

                if parent_excel_col is not None:
                    excel_cell = f"{parent_excel_col}{parent_excel_row+i}"
                    excel_cell_risk = f"{parent_excel_col}{parent_excel_row+i+1}"
                else:
                    excel_cell = None

                dropdown_severity = []
                alias_to_weight = {}

                for severity_key in severity_dict:
                    severity_alias = severity_dict[severity_key]["alias"]
                    severity_weight = severity_dict[severity_key]["weight"]
                    dropdown_severity.append(severity_alias)
                    alias_to_weight[severity_alias] = severity_weight

                var = tk.StringVar()
                var.set(dropdown_severity[0])

                # Store weight mapping for later use
                self.__risk_selection[f"{key}_frame"].update(
                    {mechanism_alias: {"var": var, "weights": alias_to_weight}}
                )

                ui_var = UIInpVariable(
                    frame_tag=f"{key}_frame",
                    tk_var=var,
                    rel_pos=i,
                    text_val=mechanism_alias,
                    text_descr=None,
                    drop_options=dropdown_severity,
                    excel_cell=excel_cell,
                    state="enabled",
                )
                self.ui_inp_vars.update({f"drop_{key}_1_0{i}": ui_var})

            ui_calc_var = UICalcVariable(tk.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{key}_frame": ui_calc_var})
            self.frame_info_dict["1"][f"{key}_frame"].n_row = i + 2

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

            dropdown_available_pathways_keys = self.receptor_fetcher.getter(key)[
                "available_pathways"
            ]
            dropdown_available_pathways_aliases = [
                self.receptor_aliases.getter()[key] for key in dropdown_available_pathways_keys
            ]
            pathway_var = tk.StringVar()
            pathway_var.set(dropdown_available_pathways_aliases[0])

            receptor_param = tk.StringVar()
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
                excel_cell=f"{parent_excel_col}{parent_excel_row+1}",
                state="enabled",
            )
            self.ui_inp_vars.update({f"drop_{key}_1_0": ui_var_pathway})
            self.ui_inp_vars.update({f"drop_{key}_1_1": ui_var_receptor_param})

            # always two rows in receptor dropdown
            excel_cell_risk = f"{parent_excel_col}{parent_excel_row+2}"
            ui_calc_var = UICalcVariable(tk.StringVar(value="0.0"), excel_cell_risk)
            self.ui_calc_vars.update({f"{key}_frame": ui_calc_var})
            self.frame_info_dict["1"][f"{key}_frame"].n_row = 3

    def __create_new_tab(self, frame_tag, frame_title):

        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=frame_title)
        self.__source_pathway_frame_creator(tab, frame_tag, frame_title)

    def __calculate_source_pathway_risk(self, frame: tk.Frame, frame_tag: str):
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

    def __source_pathway_frame_creator(self, frame, frame_tag: str, frame_title: str) -> tk.Frame:
        """ """
        for dropdown_key in self.ui_inp_vars:
            if self.ui_inp_vars[dropdown_key].frame_tag == frame_tag:
                self.general_template_dropdown(frame, dropdown_key)

        self.__btn_calculate_risk(frame, frame_tag, self.__calculate_source_pathway_risk)
        self.__light_bulb(frame, frame_tag, "white")

        return frame

    def __btn_calculate_risk(self, frame: tk.Frame, frame_tag: str, btn_command):

        calculate_btn = tk.Button(
            frame,
            bg=self.ui_settings.ui_btn_bg_color_1,
            fg=self.ui_settings.ui_btn_font_color_1,
            text="Calculate risk",
            command=lambda: btn_command(frame, frame_tag),
        )

        calculate_btn.grid(
            row=self.frame_info_dict["1"][frame_tag].n_row - 1,
            rowspan=2,
            column=0,
            sticky="nsew",
        )

    def __light_bulb(self, frame: tk.Frame, frame_tag: str, color: str) -> None:
        """ """
        light = tk.Label(frame, text=f"{self.ui_calc_vars[frame_tag].tk_var.get()}", bg=color)
        light.grid(
            row=self.frame_info_dict["1"][frame_tag].n_row - 1,
            rowspan=2,
            column=1,
            sticky="nsew",
        )

    def __create_frame_tags_titles(self, case: str, keys: list[str]):

        frame_tags_titles = []
        if case == "source" or case == "pathway":
            for risk_key in keys:
                frame_tag = f"{risk_key}_frame"
                frame_title = f"{self.hazard_fetcher.getter(risk_key)["alias"]}"
                frame_tags_titles.append((frame_tag, frame_title))
        else:
            for risk_key in keys:
                frame_tag = f"{risk_key}_frame"
                frame_title = f"{self.__receptor_key_to_alias[risk_key[:2]]}"
                frame_tags_titles.append((frame_tag, frame_title))
        return frame_tags_titles

    def ui(self, case: str, keys: list[str]):

        frame_tags_titles = self.__create_frame_tags_titles(case, keys)
        for frame_tag, frame_title in frame_tags_titles:
            self.__create_new_tab(frame_tag, frame_title)
