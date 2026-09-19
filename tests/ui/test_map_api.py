import sys

import pytest

from rss_islandr.ui.map_ui import Api


@pytest.fixture
def api(app):
    """The interface that the map page calls, with clean map data before and after the test."""

    def reset():
        app.map_ui.polygons = []
        app.map_polygons_tb.set("")
        app.map_ui.lat = app.map_ui.lng = None
        app.map_ui.crs = None
        app.map_ui.coordinates = None

    reset()
    yield Api(app.map_ui)
    reset()


def _polygon(unique_id="a", name="P1", polygon_type="polygon"):
    return {
        "unique_id": unique_id,
        "type": polygon_type,
        "name": name,
        "coordinates": [[38.0, 54.5], [38.1, 54.6], [38.2, 54.5]],
        "area_km2": 1.2,
        "node_count": 3,
    }


def test_new_polygon_is_stored(app, api):
    """
    Steps:
    1. Send a polygon from the map page.

    Expected result:
    - The call returns True, the polygon is stored and the polygon text of the app contains it.
    """
    assert api.py_api_polygons_receiver(_polygon()) is True

    assert [polygon["name"] for polygon in app.map_ui.polygons] == ["P1"]
    assert "'name': 'P1'" in app.map_polygons_tb.get()


def test_polygon_with_the_same_id_is_updated(app, api):
    """
    Steps:
    1. Send a polygon "P1".
    2. Send a polygon with the same unique id and the name "Renamed".

    Expected result:
    - There is still one polygon and it has the new name.
    """
    api.py_api_polygons_receiver(_polygon(name="P1"))
    api.py_api_polygons_receiver(_polygon(name="Renamed"))

    assert [polygon["name"] for polygon in app.map_ui.polygons] == ["Renamed"]


def test_polygon_without_id_is_rejected(app, api):
    """
    Steps:
    1. Send a polygon that has no unique id.

    Expected result:
    - The call returns False and nothing is stored.
    """
    polygon = _polygon()
    del polygon["unique_id"]

    assert api.py_api_polygons_receiver(polygon) is False
    assert app.map_ui.polygons == []


def test_clear_removes_all_polygons(app, api):
    """
    Steps:
    1. Send two polygons.
    2. Clear the polygons.

    Expected result:
    - The call returns True, no polygon is stored and the polygon text of the app is empty.
    """
    api.py_api_polygons_receiver(_polygon("a", "P1"))
    api.py_api_polygons_receiver(_polygon("b", "P2"))

    assert api.py_api_clear_polygons() is True

    assert app.map_ui.polygons == []
    assert app.map_polygons_tb.get() == ""


def test_delete_removes_the_polygon_with_that_name_and_type(app, api):
    """
    Steps:
    1. Send the polygons "P1" and "P2".
    2. Delete "P1".

    Expected result:
    - Only "P2" remains.
    """
    api.py_api_polygons_receiver(_polygon("a", "P1"))
    api.py_api_polygons_receiver(_polygon("b", "P2"))

    assert api.py_api_delete_polygons(_polygon("a", "P1")) is True

    assert [polygon["name"] for polygon in app.map_ui.polygons] == ["P2"]


def test_stored_polygons_are_sent_back_to_the_map(app, api):
    """
    Steps:
    1. Send a polygon.
    2. Ask for the stored polygons (done by the map page when it is opened again).

    Expected result:
    - The list contains the polygon.
    """
    api.py_api_polygons_receiver(_polygon())

    assert [polygon["name"] for polygon in api.py_api_send_polygons_to_js()] == ["P1"]


def test_coordinates_of_the_map_are_stored(app, api):
    """
    Steps:
    1. Send the coordinates 54.5733, 38.0048 and the CRS "EPSG:4326" from the map page.

    Expected result:
    - The app stores them as one value (latitude, longitude, CRS) for the Site info page.
    """
    api.py_api_coord_receiver(54.5733, 38.0048, "EPSG:4326")

    assert app.map_ui.coordinates == (54.5733, 38.0048, "EPSG:4326")


def test_coordinates_are_sent_to_the_map_as_numbers(app, api):
    """
    Steps:
    1. Set the latitude and longitude as text, as they are stored in the Site info fields, and a CRS.
    2. Ask for the coordinates (done by the map page when it is opened).

    Expected result:
    - The latitude and longitude are returned as numbers together with the CRS.
    """
    app.map_ui.lat, app.map_ui.lng, app.map_ui.crs = "54.5733", "38.0048", "EPSG:4326"

    assert api.py_api_send_coordinates_to_js() == (54.5733, 38.0048, "EPSG:4326")


def test_empty_coordinates_are_sent_as_none(app, api):
    """
    Steps:
    1. Leave the latitude and longitude empty.
    2. Ask for the coordinates.

    Expected result:
    - The latitude and longitude are None, so the map shows no marker.
    """
    app.map_ui.lat, app.map_ui.lng, app.map_ui.crs = "", "", ""

    assert api.py_api_send_coordinates_to_js() == (None, None, "")


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
