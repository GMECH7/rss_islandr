import sys

import pytest

from rss_islandr.assessment.risk_assessment import risk_color_assignment


@pytest.mark.parametrize(
    ("risk", "color"),
    [
        (0.05, "success"),
        (0.10, "success"),
        (0.11, "warning"),
        (0.30, "warning"),
        (0.31, "danger"),
        (1.0, "danger"),
    ],
)
def test_risk_is_assigned_to_the_right_color_band(risk, color):
    """
    Steps:
    1. Assign a color to a risk value: 0.05, 0.10, 0.11, 0.30, 0.31 and 1.0 (one test run for each).

    Expected result:
    - Up to and including 0.10 the color is "success" (green), above it up to and including 0.30 "warning"
      (yellow) and above 0.30 "danger" (red).
    """
    assert risk_color_assignment(risk) == color


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
