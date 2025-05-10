import base64
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import ttkbootstrap as tb
import webview

from rss_islandr.core.config_parser import SAVED_MAPS_IMAGES_DIR

logging.basicConfig(level=logging.INFO)


class Api:
    def __init__(self, map_ui_instance):
        self.map_ui = map_ui_instance  # Reference to MapUI instance

    def send_coordinates(self, lat, lng):
        self.map_ui.coordinates = (lat, lng)  # Store received coordinates
        logging.info(f"Received from HTML: Latitude={lat}, Longitude={lng}")

    def receive_image_data(self, image_data):
        """Save the base64-encoded image to a file."""
        try:
            # Remove the "data:image/png;base64," prefix
            header, encoded = image_data.split(",", 1)

            # Decode the base64 data
            img_data = base64.b64decode(encoded)

            # Generate a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = SAVED_MAPS_IMAGES_DIR / f"map_export_{timestamp}.png"

            # Save to disk
            with open(filename, "wb") as f:
                f.write(img_data)

            logging.info(f"Image saved as: {filename}")
        except Exception as e:
            logging.error(f"Failed to save image: {e}")


class MapUI:
    def __init__(self, map_html: Path, style: tb.Style, map_height: int, map_width: int):
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
        webview.start(debug=False)
