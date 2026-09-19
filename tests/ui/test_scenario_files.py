import json
import sys
from tkinter import filedialog, messagebox

import pytest

from rss_islandr.ui.io_btns import ExportScenarioBtn, ImportScenarioBtn

POLYGONS = "[{'unique_id': 'a', 'type': 'polygon', 'name': 'P1', 'coordinates': [[1.0, 2.0]], 'area_km2': 1.2}]"


@pytest.fixture
def dialogs(monkeypatch):
    """Replace the message boxes by recorders. Returns the recorded (info, error) messages."""
    info, errors = [], []
    monkeypatch.setattr(messagebox, "showinfo", lambda *args, **kwargs: info.append(args))
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: errors.append(args))
    return info, errors


@pytest.fixture(autouse=True)
def restore_app(app, restore_inputs):
    """Restore the inputs and the polygons of the shared app after the test."""
    yield
    app.map_polygons_tb.set("")
    app.map_ui.polygons = []


def _export(app, monkeypatch, file):
    monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **kwargs: str(file))
    ExportScenarioBtn(app.ui_inp_vars, app.ui_calc_vars, map_polygons_tb=app.map_polygons_tb).on_btn_click()


def _import(app, monkeypatch, file):
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **kwargs: str(file))
    ImportScenarioBtn(
        app.ui_inp_vars, app.ui_calc_vars, map_ui=app.map_ui, map_polygons_tb=app.map_polygons_tb
    ).on_btn_click()


def test_scenario_is_saved_with_inputs_results_and_polygons(app, dialogs, monkeypatch, tmp_path):
    """
    Steps:
    1. Enter a site name, a toxicity and an extent, and set a polygon.
    2. Export the scenario to a file.

    Expected result:
    - The file is a JSON object with the value of every input field, the calculated results and the polygons.
    - A success message is shown.
    """
    app.ui_inp_vars["val_0_00"].tk_var.set("Test site")
    app.ui_inp_vars["drop_on-on_IN_1_00"].tk_var.set("Toxic metals")
    app.ui_inp_vars["drop_on-on_IN_1_01"].tk_var.set("Medium")
    app.map_polygons_tb.set(POLYGONS)
    file = tmp_path / "scenario.json"

    _export(app, monkeypatch, file)

    saved = json.loads(file.read_text(encoding="utf-8"))
    assert saved["val_0_00"] == "Test site"
    assert saved["drop_on-on_IN_1_00"] == "Toxic metals"
    assert float(saved["IN_on-on_frame"]) == pytest.approx(0.7)
    assert saved["polygons_data"] == POLYGONS
    assert set(app.ui_inp_vars) <= set(saved)
    assert len(dialogs[0]) == 1 and dialogs[1] == []


def test_imported_scenario_restores_inputs_results_and_polygons(app, dialogs, monkeypatch, tmp_path):
    """
    Steps:
    1. Enter a site name, a toxicity and an extent, set a polygon and export the scenario.
    2. Change all of them.
    3. Import the file.

    Expected result:
    - The inputs, the calculated hazard and the polygons have the values of the file again.
    """
    app.ui_inp_vars["val_0_00"].tk_var.set("Test site")
    app.ui_inp_vars["drop_on-on_IN_1_00"].tk_var.set("Toxic metals")
    app.ui_inp_vars["drop_on-on_IN_1_01"].tk_var.set("Medium")
    app.map_polygons_tb.set(POLYGONS)
    file = tmp_path / "scenario.json"
    _export(app, monkeypatch, file)
    app.ui_inp_vars["val_0_00"].tk_var.set("Other site")
    app.ui_inp_vars["drop_on-on_IN_1_00"].tk_var.set("Value Not Known")
    app.map_polygons_tb.set("")

    _import(app, monkeypatch, file)

    assert app.ui_inp_vars["val_0_00"].tk_var.get() == "Test site"
    assert app.ui_inp_vars["drop_on-on_IN_1_00"].tk_var.get() == "Toxic metals"
    assert float(app.ui_calc_vars["IN_on-on_frame"].tk_var.get()) == pytest.approx(0.7)
    assert app.map_polygons_tb.get() == POLYGONS
    assert app.map_ui.polygons[0]["name"] == "P1"
    assert dialogs[1] == []


def test_import_of_an_incomplete_file_shows_an_error(app, dialogs, monkeypatch, tmp_path):
    """
    Steps:
    1. Create a scenario file that has no input values.
    2. Import it.

    Expected result:
    - An error message is shown and no success message.
    """
    file = tmp_path / "incomplete.json"
    file.write_text("{}", encoding="utf-8")

    _import(app, monkeypatch, file)

    assert dialogs[0] == []
    assert len(dialogs[1]) == 1


def test_import_of_a_file_that_is_not_json_shows_an_error(app, dialogs, monkeypatch, tmp_path):
    """
    Steps:
    1. Create a text file that is not JSON.
    2. Import it.

    Expected result:
    - An error message is shown and the inputs are unchanged.
    """
    file = tmp_path / "text.json"
    file.write_text("not json", encoding="utf-8")
    app.ui_inp_vars["val_0_00"].tk_var.set("Test site")

    _import(app, monkeypatch, file)

    assert len(dialogs[1]) == 1
    assert app.ui_inp_vars["val_0_00"].tk_var.get() == "Test site"


def test_cancelled_dialogs_do_nothing(app, dialogs, monkeypatch, tmp_path):
    """
    Steps:
    1. Export a scenario and cancel the file dialog.
    2. Import a scenario and cancel the file dialog.

    Expected result:
    - No file is written, no message is shown and the inputs are unchanged.
    """
    app.ui_inp_vars["val_0_00"].tk_var.set("Test site")

    _export(app, monkeypatch, "")
    _import(app, monkeypatch, "")

    assert dialogs == ([], [])
    assert app.ui_inp_vars["val_0_00"].tk_var.get() == "Test site"
    assert list(tmp_path.iterdir()) == []


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
