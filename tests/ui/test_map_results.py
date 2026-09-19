import sys
import threading

import pytest


def _open_map(app, monkeypatch, coordinates=None, polygons=None):
    """Run the code behind the 'Maps Viewer' button with a fake map that sets some results."""

    def fake_run_webview():
        app.map_ui.coordinates = coordinates
        app.map_ui.polygons = polygons or []

    monkeypatch.setattr(app.map_ui, "run_webview", fake_run_webview)
    app._MainAppUI__toggle_map()


def test_coordinates_of_the_map_are_taken_over(app, monkeypatch):
    """
    Steps:
    1. Replace the map window by a fake that returns the coordinates 54.5733, 38.0048 (EPSG:4326).
    2. Click 'Maps Viewer' (run the code behind the button).

    Expected result:
    - Site info has the CRS 'EPSG:4326', the latitude '54.5733' and the longitude '38.0048'.
    """
    _open_map(app, monkeypatch, coordinates=(54.5733, 38.0048, "EPSG:4326"))

    assert app.ui_inp_vars["map_0_00"].tk_var.get() == "EPSG:4326"
    assert app.ui_inp_vars["map_0_01"].tk_var.get() == "54.5733"
    assert app.ui_inp_vars["map_0_02"].tk_var.get() == "38.0048"


def test_polygons_of_the_map_are_taken_over(app, monkeypatch):
    """
    Steps:
    1. Clear the polygons of the app.
    2. Replace the map window by a fake that returns one polygon 'P1'.
    3. Click 'Maps Viewer'.

    Expected result:
    - The polygon data of the app contains the polygon 'P1'.
    """
    app.map_polygons_tb.set("")
    polygon = {"unique_id": "a", "type": "polygon", "name": "P1", "coordinates": [[1, 2]], "area_km2": 1.2}

    _open_map(app, monkeypatch, polygons=[polygon])

    assert "'name': 'P1'" in app.map_polygons_tb.get()


def test_opening_the_map_does_not_start_threads(app, monkeypatch):
    """
    Steps:
    1. Count the running threads.
    2. Click 'Maps Viewer' twice (with a fake map window).
    3. Count the running threads again.

    Expected result:
    - The number of threads is the same: opening the map does not leave a polling thread behind.
    """
    threads_before = threading.active_count()

    _open_map(app, monkeypatch)
    _open_map(app, monkeypatch)

    assert threading.active_count() == threads_before


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
