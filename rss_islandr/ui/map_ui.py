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

    def send_coordinates(self, lat, lng):
        self.map_ui.coordinates = (lat, lng)  # Store received coordinates
        logging.info(f"Received from HTML: Latitude={lat}, Longitude={lng}")

    def send_drawing(self, *args, **kwargs):
        pass


class MapUI:
    def __init__(self, map_html: Path, style: tb.Style):
        self.__style = style
        self.map_html = map_html
        self.webview_process = None
        self.coordinates = None  # Stores latest latitude and longitude

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
        logging.info("Webview started. Waiting for coordinates...")
        # Set the webview settings to avoid opening devtools when debugging is True
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = True
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.start(debug=True)
