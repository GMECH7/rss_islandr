import json
import sys
from types import SimpleNamespace

import pytest

from rss_islandr.ui import map_ui
from rss_islandr.ui.map_ui import MapUI, _ChildMapState

POLYGON = {"unique_id": "a", "type": "polygon", "name": "P1", "coordinates": [[1, 2]], "area_km2": 1.2}


@pytest.fixture
def clean_map(app):
    """The map data of the app, cleaned before and after the test."""

    def reset():
        app.map_ui.polygons = []
        app.map_polygons_tb.set("")
        app.map_ui.coordinates = None
        app.map_ui.lat = app.map_ui.lng = app.map_ui.crs = None

    reset()
    yield app.map_ui
    reset()


def _fake_map_process(state, return_code=0, payloads=None):
    """A replacement of `subprocess.run` that acts as the map process: it saves `state` as its result."""

    def run(command, input=None, **kwargs):
        payload = json.loads(input)
        if payloads is not None:
            payloads.append((command, payload))
        if state is not None:
            with open(payload["result_file"], "w", encoding="utf-8") as result_file:
                json.dump(state, result_file)
        return SimpleNamespace(returncode=return_code)

    return run


def test_child_state_is_saved_when_it_changes(tmp_path):
    """
    Steps:
    1. Create the state of the map process with one polygon.
    2. Set coordinates and replace the polygons.

    Expected result:
    - The result file always contains the current polygons and coordinates, so nothing is lost if the process
      crashes.
    """
    result_file = tmp_path / "state.json"
    payload = {"result_file": str(result_file), "polygons": [POLYGON], "lat": None, "lng": None, "crs": ""}

    state = _ChildMapState(payload)
    state.coordinates = (54.5, 38.0, "EPSG:4326")
    assert json.loads(result_file.read_text()) == {"polygons": [POLYGON], "coordinates": [54.5, 38.0, "EPSG:4326"]}

    state.polygons = []
    assert json.loads(result_file.read_text())["polygons"] == []


def test_child_state_saves_when_the_polygon_text_is_set(tmp_path):
    """
    Steps:
    1. Create the state of the map process.
    2. Add a polygon to the list and set the polygon text (as the map interface does).

    Expected result:
    - The result file contains the new polygon.
    """
    result_file = tmp_path / "state.json"
    state = _ChildMapState({"result_file": str(result_file), "polygons": [], "lat": None, "lng": None, "crs": ""})

    state.polygons.append(POLYGON)
    state.map_polygons_tb.set("text")

    assert json.loads(result_file.read_text())["polygons"] == [POLYGON]


def test_map_results_are_taken_over_from_the_map_process(app, clean_map, monkeypatch):
    """
    Steps:
    1. Pretend to run on Linux with a map process that returns coordinates and one polygon.
    2. Open the map.

    Expected result:
    - The polygons, the polygon text and the coordinates of the app are those of the map process.
    """
    state = {"polygons": [POLYGON], "coordinates": [54.5, 38.0, "EPSG:4326"]}
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(map_ui.subprocess, "run", _fake_map_process(state))

    clean_map.run_webview()

    assert clean_map.polygons == [POLYGON]
    assert "'name': 'P1'" in app.map_polygons_tb.get()
    assert clean_map.coordinates == (54.5, 38.0, "EPSG:4326")


def test_map_process_gets_the_current_polygons_and_coordinates(app, clean_map, monkeypatch):
    """
    Steps:
    1. Set a polygon, coordinates and a CRS in the app.
    2. Open the map with a fake map process that records what it receives.

    Expected result:
    - The process receives the polygon, the coordinates, the CRS, the map page and the file for its result.
    """
    clean_map.polygons = [POLYGON]
    clean_map.lat, clean_map.lng, clean_map.crs = "54.5", "38.0", "EPSG:4326"
    payloads = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(map_ui.subprocess, "run", _fake_map_process({"polygons": [], "coordinates": None}, 0, payloads))

    clean_map.run_webview()

    payload = payloads[0][1]
    assert payload["polygons"] == [POLYGON]
    assert (payload["lat"], payload["lng"], payload["crs"]) == ("54.5", "38.0", "EPSG:4326")
    assert payload["map_html"].endswith("index.html")
    assert payload["result_file"].endswith("map_state.json")


def test_work_of_a_crashed_map_process_is_kept(app, clean_map, monkeypatch):
    """
    Steps:
    1. Pretend to run on Linux with a map process that saved one polygon and then crashed (exit code -11).
    2. Open the map.

    Expected result:
    - The application keeps running and the polygon is taken over.
    """
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(map_ui.subprocess, "run", _fake_map_process({"polygons": [POLYGON], "coordinates": None}, -11))

    clean_map.run_webview()

    assert clean_map.polygons == [POLYGON]


def test_missing_result_of_the_map_process_changes_nothing(app, clean_map, monkeypatch):
    """
    Steps:
    1. Set a polygon in the app.
    2. Open the map with a map process that fails without saving a result.

    Expected result:
    - No error is raised and the polygon is unchanged.
    """
    clean_map.polygons = [POLYGON]
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(map_ui.subprocess, "run", _fake_map_process(None, 1))

    clean_map.run_webview()

    assert clean_map.polygons == [POLYGON]


def test_map_process_that_cannot_start_shows_an_error(app, clean_map, monkeypatch):
    """
    Steps:
    1. Pretend to run on Linux where starting the map process fails.
    2. Open the map.

    Expected result:
    - An error message with the reason is shown and the application keeps running.
    """
    errors = []

    def cannot_start(*args, **kwargs):
        raise OSError("no such file")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(map_ui.subprocess, "run", cannot_start)
    monkeypatch.setattr(map_ui.messagebox, "showerror", lambda *args, **kwargs: errors.append(args))

    clean_map.run_webview()

    assert len(errors) == 1
    assert "no such file" in errors[0][1]


def test_map_runs_in_the_application_process_on_windows(app, clean_map, monkeypatch):
    """
    Steps:
    1. Pretend to run on Windows and replace the map window by a fake.
    2. Open the map.

    Expected result:
    - The map window is opened in the application process and no separate process is started.
    """
    calls = []
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(MapUI, "_MapUI__run_webview_in_process", lambda self: calls.append("in process"))
    monkeypatch.setattr(map_ui.subprocess, "run", lambda *args, **kwargs: calls.append("subprocess"))

    clean_map.run_webview()

    assert calls == ["in process"]


def test_map_process_command_of_the_installed_application(monkeypatch):
    """
    Steps:
    1. Ask for the command of the map process when running from source and when running as the installed application.

    Expected result:
    - From source the command runs a small piece of Python code. The installed application starts itself with
      `--map-process`.
    """
    command = MapUI._MapUI__map_process_command

    monkeypatch.delattr(sys, "frozen", raising=False)
    assert command() == [sys.executable, "-c", map_ui.MAP_PROCESS_CODE]

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert command() == [sys.executable, "--map-process"]


def test_coordinates_are_read_from_the_site_info_fields(app, clean_map):
    """
    Steps:
    1. Set the CRS, latitude and longitude fields of the Site info page.
    2. Update the coordinates of the map data (done after a scenario is imported).

    Expected result:
    - The map data has the values of the fields.
    """
    app.ui_inp_vars["map_0_00"].tk_var.set("EPSG:4326")
    app.ui_inp_vars["map_0_01"].tk_var.set("54.5")
    app.ui_inp_vars["map_0_02"].tk_var.set("38.0")

    clean_map.update_coordinates()

    assert (clean_map.crs, clean_map.lat, clean_map.lng) == ("EPSG:4326", "54.5", "38.0")
    for key in ("map_0_00", "map_0_01", "map_0_02"):
        app.ui_inp_vars[key].tk_var.set("")


def test_polygons_are_read_from_the_polygon_text(app, clean_map):
    """
    Steps:
    1. Set the polygon text of the app to a list with one polygon.
    2. Update the polygons of the map data (done after a scenario is imported).

    Expected result:
    - The map data contains the polygon.
    """
    app.map_polygons_tb.set(f"[{POLYGON}]")

    clean_map.update_polygons_from_stringvar()

    assert clean_map.polygons == [POLYGON]


def test_invalid_polygon_text_is_ignored(app, clean_map):
    """
    Steps:
    1. Set the polygon text to a text that cannot be read ("{'name': }") and the map data to one polygon.
    2. Update the polygons of the map data.

    Expected result:
    - No error is raised and the polygons are unchanged.
    """
    clean_map.polygons = [POLYGON]
    app.map_polygons_tb.set("{'name': }")

    clean_map.update_polygons_from_stringvar()

    assert clean_map.polygons == [POLYGON]


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
