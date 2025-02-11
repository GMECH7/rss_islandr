import json
from typing import Optional


class RisksDataFetcher:

    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.__data = json.load(file)  # Load JSON into a Python dictionary

    def __get_hazard_pathway(self, hazard_pathway_key: str):

        return self.__data[hazard_pathway_key]

    def __get_mechanism(self, hazard_pathway_key: str, mechanism_key: str):

        mechanism = self.__data[hazard_pathway_key]["mechanism"][mechanism_key]

        return mechanism

    def __get_severity(self, hazard_pathway_key: str, mechanism_key: str, severity_key: str):

        severity = self.__data[hazard_pathway_key]["mechanism"][mechanism_key]["severity"][
            severity_key
        ]

        return severity

    def getter(
        self,
        main_key: str,
        mechanism_key: Optional[str] = None,
        severity_key: Optional[str] = None,
    ):

        if mechanism_key is None and severity_key is not None:
            raise Exception

        if mechanism_key is not None and severity_key is not None:
            return self.__get_severity(main_key, mechanism_key, severity_key)
        elif mechanism_key is not None:
            return self.__get_mechanism(main_key, mechanism_key)
        else:
            return self.__get_hazard_pathway(main_key)


class ReceptorFactorsFetcher:

    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.__data = json.load(file)  # Load JSON into a Python dictionary

    def __get_pathway(self, pathway_key: str):

        return self.__data[pathway_key]

    def __get_parameter(self, pathway_key: str, parameter_key: str):

        return self.__data[pathway_key]["parameter"][parameter_key]

    def getter(self, pathway_key: str, parameter_key: Optional[str] = None):

        if parameter_key is not None:
            return self.__get_parameter(pathway_key, parameter_key)
        else:
            return self.__get_pathway(pathway_key)
