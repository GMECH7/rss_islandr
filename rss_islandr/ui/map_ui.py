# -*- coding: utf-8 -*-
import logging
import subprocess
import sys
from pathlib import Path

import ttkbootstrap as tb
import webview

logging.basicConfig(level=logging.INFO)


class Api:
    def __init__(self, map_ui_instance):
        self.map_ui = map_ui_instance  # Reference to MapUI instance

    def py_api_coord_receiver(self, lat, lng):
        """Receive coordinates from JavaScript"""
        self.map_ui.coordinates = (lat, lng)  # Store received coordinates
        logging.debug(f"Received from HTML: Latitude={lat}, Longitude={lng}")

    def py_api_polygons_receiver(self, feature_data):
        """Receive polygon data from JavaScript"""

        logging.debug(f"Received polygon data: {feature_data}")

        # Ensure unique_id exists
        if "unique_id" not in feature_data:
            logging.error("Received polygon without unique_id!")
            return False

        # Check if this polygon already exists
        existing_index = None
        for i, poly in enumerate(self.map_ui.polygons):
            if poly.get("unique_id") == feature_data["unique_id"]:
                existing_index = i
                break

        # Create the polygon data structure
        polygon = {
            "unique_id": feature_data["unique_id"],
            "type": feature_data["type"],
            "name": feature_data["name"],
            "coordinates": feature_data["coordinates"],
            "area_km2": feature_data["area_km2"],
            "node_count": feature_data["node_count"],
        }

        if existing_index is not None:
            # Update existing polygon
            self.map_ui.polygons[existing_index] = polygon
            logging.debug(f"Updated existing polygon: {polygon}")
        else:
            # Add new polygon
            self.map_ui.polygons.append(polygon)
            logging.debug(f"Added new polygon: {polygon}")

        return True

    def py_api_clear_polygons(self):
        """Clear all stored polygons"""
        logging.debug("Clearing all polygons from storage")
        self.map_ui.polygons = []  # Empty the list

        return True

    def py_api_delete_polygons(self, feature_data):
        """Delete a polygon from storage"""
        logging.debug(f"Deleting polygon: {feature_data}")

        # Remove the polygon by name and type
        self.map_ui.polygons = [
            poly
            for poly in self.map_ui.polygons
            if not (poly["name"] == feature_data["name"] and poly["type"] == feature_data["type"])
        ]

        logging.debug(f"Remaining polygons: {len(self.map_ui.polygons)}")
        return True

    def py_api_send_polygons_to_js(self):
        """Return all stored polygons to JavaScript for redrawing"""
        logging.debug(f"Polygons sent to js {self.map_ui.polygons}")
        return self.map_ui.polygons


class MapUI:
    def __init__(self, map_html: Path, style: tb.Style):
        self.__style = style
        self.map_html = map_html
        self.webview_process = None
        self.coordinates = None  # Stores latest latitude and longitude
        self.polygons = []

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
        self.coordinates = None  # Reset after reading
        return coords

    def get_polygons_data(self) -> str:
        """Retrieve the polygons data collected from the webview."""
        map_polygons_data = ""
        for polygon in self.polygons:
            map_polygons_data += f"{polygon}"

        return map_polygons_data

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
