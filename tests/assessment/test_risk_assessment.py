import sys

import pytest

from rss_islandr.assessment.risk_assessment import risk_calc, risk_color_assignment


def test_risk_calc():
    """
    Steps:
    1. Call `risk_calc` with three weight lists: [1.0, 1.0, 1.0], [0.5, 1.0, 0.5] and [0.1, 0.2, 0.3, 0.0].

    Expected result:
    - The results are the products of the weights: 1.0, 0.25 and 0.0 (one weight of 0 gives a risk of 0).
    """
    assert risk_calc([1.0, 1.0, 1.0]) == 1.0
    assert risk_calc([0.5, 1.0, 0.5]) == 0.25
    assert risk_calc([0.1, 0.2, 0.3, 0.0]) == 0.0


def test_risk_color_assignment():
    """
    Steps:
    1. Call `risk_color_assignment` with the risk value 0.5.

    Expected result:
    - A colour name (a string) is returned. The test does not check which colour band the value belongs to.
    """
    assert isinstance(risk_color_assignment(0.5), str)


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
