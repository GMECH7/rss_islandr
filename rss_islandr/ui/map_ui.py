# -*- coding: utf-8 -*-
import contextlib
import logging
import subprocess
import sys
from pathlib import Path

import ttkbootstrap as tb
import webview

from rss_islandr.core.datatypes import PolygonDataDict
from rss_islandr.core.helpers import extract_dicts_from_string

logging.basicConfig(level=logging.INFO)


class Api:
    def __init__(self, map_ui_instance):
        self.map_ui = map_ui_instance

    def py_api_coord_receiver(self, lat: float, lng: float, crs: str):
        """Receive coordinates from JavaScript"""
        self.map_ui.coordinates = (lat, lng, crs)  # Store received coordinates
        logging.debug(f"Received coordinates: Latitude={lat}, Longitude={lng}, CRS={crs}")

    def py_api_polygons_receiver(self, polygon_data: PolygonDataDict):
        """
        Receive polygon data from JavaScript.
        """
        logging.debug(f"Received polygon data: {polygon_data}")

        # Ensure unique_id exists
        if "unique_id" not in polygon_data:
            logging.error("Received polygon without unique_id!")
            return False

        # Check if this polygon already exists
        existing_index = None
        for i, poly in enumerate(self.map_ui.polygons):
            if poly.get("unique_id") == polygon_data["unique_id"]:
                existing_index = i
                break

        # Create a copy to avoid modifying the original data
        polygon = polygon_data.copy()

        if existing_index is not None:
            # Update existing polygon
            self.map_ui.polygons[existing_index] = polygon
            logging.debug(f"Updated existing polygon: {polygon}")
        else:
            # Add new polygon
            self.map_ui.polygons.append(polygon)
            logging.debug(f"Added new polygon: {polygon}")

        self.map_ui.map_polygons_tb.set(f"{self.map_ui.polygons}")
        return True

    def py_api_clear_polygons(self):
        """Clear all stored polygons"""
        logging.debug("Clearing all polygons from storage")
        self.map_ui.polygons = []  # Empty the list
        self.map_ui.map_polygons_tb.set("")  # Clear the StringVar
        return True

    def py_api_delete_polygons(self, polygon_data: PolygonDataDict):
        """Delete a polygon from storage based on its unique_id and type"""
        logging.debug(f"Deleting polygon: {polygon_data}")

        # Keep polygons that do not match the given polygon_data
        self.map_ui.polygons = [
            poly
            for poly in self.map_ui.polygons
            if not (poly["name"] == polygon_data["name"] and poly["type"] == polygon_data["type"])
        ]

        logging.debug(f"Remaining polygons: {len(self.map_ui.polygons)}")
        return True

    def py_api_send_polygons_to_js(self):
        """Return all stored polygons to JavaScript for redrawing"""
        logging.debug(f"Polygons sent to js: {self.map_ui.polygons}")
        return self.map_ui.polygons

    def py_api_send_coordinates_to_js(self) -> tuple[float | None, float | None, str]:
        """Return the latest coordinates to JavaScript"""
        logging.debug(f"Coordinates sent to JavaScript: {self.map_ui.lat}, {self.map_ui.lng}")
        if self.map_ui.lat is None or self.map_ui.lat == "":
            self.map_ui.lat = None
            self.map_ui.crs = "EPSG:4326"
        else:
            self.map_ui.lat = float(self.map_ui.lat)

        if self.map_ui.lng is None or self.map_ui.lng == "":
            self.map_ui.lng = None
            self.map_ui.crs = "EPSG:4326"
        else:
            self.map_ui.lng = float(self.map_ui.lng)

        return self.map_ui.lat, self.map_ui.lng, self.map_ui.crs


class MapUI:
    def __init__(self, map_html: Path, style: tb.Style, ui_inp_vars, map_polygons_tb: tb.StringVar):
        self.__style = style
        self.map_html = map_html
        self.webview_process = None
        self.ui_inp_vars = ui_inp_vars
        self.coordinates = None
        self.map_polygons_tb = map_polygons_tb  # StringVar to hold polygon data as a string and 'live' throught app
        self.polygons = []  # list of PolygonDataDict used in class

        self.lat = None
        self.lng = None
        self.crs = "EPSG:4326"

    def update_coordinates(self):
        """
        Update coordinates (self.coordinates) from StringVar content.

        This methood is called in the following cases:
        1. When a scenario is imported.
        2. When restoring defaults in the main app UI.
        """
        self.lat = self.ui_inp_vars.get("map_0_01").tk_var.get()
        self.lng = self.ui_inp_vars.get("map_0_02").tk_var.get()
        self.crs = self.ui_inp_vars.get("map_0_00").tk_var.get()

    def update_polygons_from_stringvar(self):
        """
        Update polygons (self.polygons) from StringVar content.

        This methood is called in the following cases:
        1. When a scenario is imported.
        2. When restoring defaults in the main app UI.
        """
        map_polygons_value = self.map_polygons_tb.get()

        try:
            extracted = extract_dicts_from_string(map_polygons_value)
            self.polygons = extracted
            logging.debug(f"Updated polygons from import: {self.polygons}")
        except Exception as e:
            logging.error(f"Error parsing polygons from StringVar: {e}")

    def show_map(self):
        """Launch the webview window in a separate process."""
        self.webview_process = subprocess.Popen([sys.executable, __file__, "--webview"])

    def close_map(self):
        """Terminate the webview process."""
        if self.webview_process:
            self.webview_process.terminate()
            self.webview_process = None

    def get_coordinates(self):
        """Retrieve the latest coordinates and reset them after reading."""
        coords = self.coordinates
        with contextlib.suppress(Exception):
            self.lat, self.lng, self.crs = coords
        self.coordinates = None  # Reset after reading
        return coords

    def get_polygons_data(self) -> str:
        """
        Retrieve the polygons data collected from the webview
        and format it as a string for further manipulation in python
        """
        map_polygons_as_str = ""
        for polygon in self.polygons:
            map_polygons_as_str += f"{polygon}"

        return map_polygons_as_str

    def run_webview(self):
        """Run the webview window (to be called in a separate process)."""
        api_instance = Api(self)  # Create API instance linked to MapUI
        webview.create_window(
            "Maps Viewer",
            str(self.map_html),
            width=1600,
            height=900,
            background_color=self.__style.colors.bg,
            js_api=api_instance,  # Attach the JavaScript API
        )
        logging.debug("Webview started. Waiting for coordinates...")
        # Set the webview settings to avoid opening devtools when debugging is True
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.start(debug=True)
