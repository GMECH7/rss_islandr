import sys

import pytest
import ttkbootstrap as tb

pytestmark = pytest.mark.usefixtures("restore_inputs")


def _widgets(widget):
    for child in widget.winfo_children():
        yield child
        yield from _widgets(child)


def _status_combobox(app):
    status_variable = str(app.ui_inp_vars["drop_0_01"].tk_var)
    return next(
        widget
        for widget in _widgets(app._site_info_page)
        if widget.winfo_class() == "TCombobox" and str(widget.cget("textvariable")) == status_variable
    )


def _operation_dates(app):
    """The start and the end date of the operation (the first date entry of the page is the assessment date)."""
    entries = [widget for widget in _widgets(app._site_info_page) if isinstance(widget, tb.DateEntry)]
    return entries[1], entries[2]


def _grid(widget):
    info = widget.grid_info()
    return int(info["row"]), int(info["column"])


def test_active_status_shows_the_start_date_below_the_status(app):
    """
    Steps:
    1. Select the site status "Active" on the Site info page.

    Expected result:
    - The start date is shown in the row below the site status. The site status dropdown stays in its own row
      and is not covered, so it can be used again.
    """
    app.ui_inp_vars["drop_0_01"].tk_var.set("Active")
    app._site_info_page.update()

    status_row, status_column = _grid(_status_combobox(app))
    start_date, _ = _operation_dates(app)
    assert start_date.winfo_manager() == "grid"
    assert _grid(start_date)[0] == status_row + 1
    assert (status_row, status_column) == (8, 1)


def test_legacy_status_shows_start_and_end_dates_below_the_status(app):
    """
    Steps:
    1. Select the site status "Legacy".

    Expected result:
    - The start date and the end date are shown side by side in the row below the site status.
    """
    app.ui_inp_vars["drop_0_01"].tk_var.set("Legacy")
    app._site_info_page.update()

    status_row = _grid(_status_combobox(app))[0]
    start_date, end_date = _operation_dates(app)
    assert _grid(start_date) == (status_row + 1, 1)
    assert _grid(end_date) == (status_row + 1, 2)


def test_site_status_can_be_changed_after_a_date_is_shown(app):
    """
    Steps:
    1. Select "Active", then "Legacy", then "Proposed" one after the other.

    Expected result:
    - The site status dropdown stays at the same place (row 8, column 1) every time and no date widget is placed
      in its row. The end date is only shown for "Legacy".
    """
    status = _status_combobox(app)
    position = _grid(status)

    for option in ("Active", "Legacy", "Proposed"):
        app.ui_inp_vars["drop_0_01"].tk_var.set(option)
        app._site_info_page.update()

        assert _grid(status) == position
        start_date, end_date = _operation_dates(app)
        assert _grid(start_date)[0] != position[0]
        assert (end_date.winfo_manager() == "grid") == (option == "Legacy")


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
