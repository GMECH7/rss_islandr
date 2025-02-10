import os
import sys
from pathlib import Path

from main_imports import rss_islandr

from rss_islandr.assessment.risk_assessment import risk_calc
from rss_islandr.data_readers import RisksDataFetcher

filepath = r"C:\Users\George\Documents\makge\Python\islandr\rss_islandr\rss_islandr\data"
filename = "risk_factors.json"

if __name__ == "__main__":

    json_file = os.path.join(filepath, filename)
    hazard_fetcher = RisksDataFetcher(json_file)

    hazard_toxicity = hazard_fetcher.getter("IN", "01", "01")["weight"]
    hazard_extend = hazard_fetcher.getter("IN", "01", "03")["weight"]
    hazard_mobility = hazard_fetcher.getter("IN", "01", "01")["weight"]

    hazard_risk = risk_calc([hazard_toxicity, hazard_extend, hazard_mobility])

    mechanisms_dict = hazard_fetcher.getter("IN")["mechanism"]
    for mechanism_key in mechanisms_dict:
        mechanism_alias = hazard_fetcher.getter("IN", mechanism_key)["alias"]
        severity_dict = hazard_fetcher.getter("IN", mechanism_key)["severity"]
        dropdown_severity = []
        alias_to_weight = {}
        for severity_key in severity_dict:
            severity_alias = severity_dict[severity_key]["alias"]
            severity_weight = severity_dict[severity_key]["weight"]
            dropdown_severity.append(severity_dict[severity_key]["alias"])
            alias_to_weight[severity_alias] = severity_weight
