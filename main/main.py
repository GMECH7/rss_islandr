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
    print(hazard_risk)
