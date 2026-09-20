import sys

import pytest

from rss_islandr.core.config_parser import RECEPTOR_FACTORS_JSON_DIR, RISK_FACTORS_JSON_DIR
from rss_islandr.data_readers import ReceptorAliases, ReceptorFactorsFetcher, RisksDataFetcher


@pytest.fixture(scope="module")
def risks():
    return RisksDataFetcher(RISK_FACTORS_JSON_DIR)


def test_hazard_or_pathway_is_read_by_its_key(risks):
    """
    Steps:
    1. Read the pathway "SL" from the risk factors.

    Expected result:
    - It is the soil pathway with its mechanisms (parameters).
    """
    soil = risks.getter("SL")

    assert soil["alias"] == "Soil"
    assert "mechanism" in soil


def test_mechanism_and_severity_are_read_by_their_keys(risks):
    """
    Steps:
    1. Read the mechanism "02" (Extent) of the source "IN".
    2. Read its severity "01" (Large).

    Expected result:
    - The mechanism is "Extent" and the severity "Large" has the weight 1.0.
    """
    assert risks.getter("IN", "02")["alias"] == "Extent"
    assert risks.getter("IN", "02", "01") == {"alias": "Large", "weight": 1.0}


def test_severity_without_mechanism_is_rejected(risks):
    """
    Steps:
    1. Ask for a severity without giving the mechanism.

    Expected result:
    - An error is raised.
    """
    with pytest.raises(Exception):
        risks.getter("IN", None, "01")


def test_unknown_key_is_rejected(risks):
    """
    Steps:
    1. Ask for a key that does not exist.

    Expected result:
    - A `KeyError` is raised.
    """
    with pytest.raises(KeyError):
        risks.getter("XX")


def test_every_parameter_starts_with_value_not_known_and_weights_are_between_0_and_1(risks):
    """
    Steps:
    1. Read all sources and pathways of the risk factors.
    2. Check the options of every parameter.

    Expected result:
    - The first option of every parameter is "Value Not Known" with the weight 0.
    - All weights are between 0 and 1.
    """
    for key in ("IN", "SL", "GW", "SW", "AR", "SD"):
        for mechanism in risks.getter(key)["mechanism"].values():
            options = list(mechanism["severity"].values())
            assert options[0] == {"alias": "Value Not Known", "weight": 0.0}
            assert all(0.0 <= option["weight"] <= 1.0 for option in options)


def test_receptor_classes_and_weights_are_read():
    """
    Steps:
    1. Read the groundwater receptor and one of its classes.

    Expected result:
    - The class "Domestic/potable" has the weight 1.0 and the receptor lists the pathways that can lead to it.
    """
    receptors = ReceptorFactorsFetcher(RECEPTOR_FACTORS_JSON_DIR)

    assert receptors.getter("GW_receptor", "02") == {"alias": "Domestic/potable", "weight": 1.0}
    assert receptors.getter("GW_receptor")["available_pathways"] == ["SL", "GW", "SW", "SD"]


def test_receptor_aliases_name_the_five_compartments():
    """
    Steps:
    1. Read the receptor aliases.

    Expected result:
    - The aliases of SL, GW, SW, AR and SD are Soil, Groundwater, Surface water, Air and Sediment.
    """
    aliases = ReceptorAliases(RECEPTOR_FACTORS_JSON_DIR).getter()

    assert aliases == {
        "SL": "Soil",
        "GW": "Groundwater",
        "SW": "Surface water",
        "AR": "Air",
        "SD": "Sediment",
    }


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
