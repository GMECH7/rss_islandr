import sys

import pytest

from rss_islandr.assessment.risk_assessment import risk_color_assignment

SCENARIO = "on-on"

pytestmark = pytest.mark.usefixtures("restore_inputs")


def _select(app, key, option):
    app.ui_inp_vars[key].tk_var.set(option)


def _risk(app, frame_tag):
    return float(app.ui_calc_vars[f"{frame_tag}_{SCENARIO}_frame"].tk_var.get())


def _set_source(app, toxicity, extent):
    _select(app, f"drop_{SCENARIO}_IN_1_00", toxicity)
    _select(app, f"drop_{SCENARIO}_IN_1_01", extent)


def _set_soil_pathway(app, *options):
    for i, option in enumerate(options):
        _select(app, f"drop_{SCENARIO}_SL_1_0{i}", option)


def _set_receptor(app, receptor, pathway, receptor_class):
    _select(app, f"drop_{receptor}_{SCENARIO}_1_0", pathway)
    _select(app, f"drop_{receptor}_{SCENARIO}_1_1", receptor_class)


def test_hazard_is_toxicity_times_extent(app):
    """
    Steps:
    1. Select the toxicity "Toxic metals" (weight 1.0) and the extent "Medium" (weight 0.7) of the source.

    Expected result:
    - The hazard of the on-site to on-site scenario is 0.7.
    """
    _set_source(app, "Toxic metals", "Medium")

    assert _risk(app, "IN") == pytest.approx(0.7)


def test_pathway_is_the_product_of_its_parameters(app):
    """
    Steps:
    1. Select the five soil parameters: High (1.0), None (1.0), Limited access (0.8), Medium (0.8), <1m (1.0).

    Expected result:
    - The soil pathway score is 1.0 x 1.0 x 0.8 x 0.8 x 1.0 = 0.64.
    """
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "<1m")

    assert _risk(app, "SL") == pytest.approx(0.64)


def test_receptor_risk_multiplies_hazard_pathway_and_receptor(app):
    """
    Steps:
    1. Select the source (hazard 0.7) and the soil parameters (pathway 0.64).
    2. Select the soil receptor with the pathway "Soil" and the class "Residential" (weight 0.5).

    Expected result:
    - The risk of the soil receptor is 0.7 x 0.64 x 0.5 = 0.224 (22.4 %), which is in the yellow band.
    """
    _set_source(app, "Toxic metals", "Medium")
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "<1m")
    _set_receptor(app, "SL_receptor", "Soil", "Residential")

    risk = _risk(app, "SL_receptor")
    assert risk == pytest.approx(0.224)
    assert risk_color_assignment(risk) == "warning"


def test_unanswered_parameter_gives_zero_risk(app):
    """
    Steps:
    1. Select all source and soil options, but leave one soil parameter (Depth to hazard) at "Value Not Known".
    2. Select the soil receptor.

    Expected result:
    - The soil pathway score and the risk of the receptor are 0.
    """
    _set_source(app, "Toxic metals", "Medium")
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "Value Not Known")
    _set_receptor(app, "SL_receptor", "Soil", "Residential")

    assert _risk(app, "SL") == 0.0
    assert _risk(app, "SL_receptor") == 0.0


def test_receptor_uses_the_pathway_that_is_selected_for_it(app):
    """
    Steps:
    1. Select the source and the soil parameters, and leave the groundwater parameters unanswered.
    2. Select the groundwater receptor ("Domestic/potable", weight 1.0) with the pathway "Soil".
    3. Change its pathway to "Groundwater".

    Expected result:
    - With the pathway "Soil" the risk is 0.7 x 0.64 x 1.0 = 0.448.
    - With the pathway "Groundwater" the risk is 0, because that pathway is unanswered.
    """
    _set_source(app, "Toxic metals", "Medium")
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "<1m")
    _set_receptor(app, "GW_receptor", "Soil", "Domestic/potable")
    assert _risk(app, "GW_receptor") == pytest.approx(0.448)

    _select(app, f"drop_GW_receptor_{SCENARIO}_1_0", "Groundwater")

    assert _risk(app, "GW_receptor") == 0.0


def test_scenarios_are_independent(app):
    """
    Steps:
    1. Select the source, the soil parameters and the soil receptor in the on-site to on-site scenario.
    2. Read the hazard and the soil receptor risk of the on-site to off-site scenario.

    Expected result:
    - The on-site to on-site scenario has a risk above 0, the on-site to off-site scenario stays at 0.
    """
    _set_source(app, "Toxic metals", "Medium")
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "<1m")
    _set_receptor(app, "SL_receptor", "Soil", "Residential")

    assert _risk(app, "SL_receptor") > 0
    assert float(app.ui_calc_vars["IN_on-off_frame"].tk_var.get()) == 0.0
    assert float(app.ui_calc_vars["SL_receptor_on-off_frame"].tk_var.get()) == 0.0


def test_meter_shows_the_risk_in_percent(app):
    """
    Steps:
    1. Select the source, the soil parameters and the soil receptor (risk 0.224).
    2. Read the meter of the soil receptor.

    Expected result:
    - The meter shows 22 % (the widget rounds to whole percent).
    """
    _set_source(app, "Toxic metals", "Medium")
    _set_soil_pathway(app, "High", "None", "Limited access", "Medium", "<1m")
    _set_receptor(app, "SL_receptor", "Soil", "Residential")

    meter = app.meter_frames[f"SL_receptor_{SCENARIO}_frame_risk"]
    assert float(meter.amountusedvar.get()) == pytest.approx(22.4, abs=0.5)


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
