import sys

import pytest

from rss_islandr import self_test


def test_risk_calculation_check_passes():
    """
    Steps:
    1. Run the risk calculation check of the self-test.

    Expected result:
    - No error is raised.
    """
    self_test.check_risk_calculation()


def test_excel_template_check_passes():
    """
    Steps:
    1. Run the Excel template check of the self-test.

    Expected result:
    - No error is raised: the template opens and has its five sheets.
    """
    self_test.check_excel_template()


def test_excel_template_check_fails_for_a_template_with_other_sheets(monkeypatch, tmp_path):
    """
    Steps:
    1. Point the check to a workbook that has one sheet.
    2. Run the Excel template check.

    Expected result:
    - An `AssertionError` is raised.
    """
    from openpyxl import Workbook

    workbook_file = tmp_path / "template.xlsx"
    Workbook().save(workbook_file)
    monkeypatch.setattr(self_test.cfg, "XLSX_TEMPLATE_FILE", workbook_file)

    with pytest.raises(AssertionError):
        self_test.check_excel_template()


def test_all_checks_are_part_of_the_self_test():
    """
    Steps:
    1. Read the list of checks of the self-test.

    Expected result:
    - It has the files, risk calculation, Excel template, web engine and main window checks, in this order.
    """
    names = [name for name, _ in self_test.CHECKS]

    assert names == [
        "data and static files",
        "risk calculation",
        "Excel template",
        "web engine of the map viewer",
        "main window",
    ]


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
