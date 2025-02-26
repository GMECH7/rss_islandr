import os
import subprocess
import sys
from pathlib import Path

CRNT_DIR = Path(__file__).parent
STATIC_DIR = CRNT_DIR.resolve().parent / "static"


import webview


class MapUI:
    def __init__(self, map_html: Path):
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

        class Api:
            def __init__(self, map_ui_instance):
                self.map_ui = map_ui_instance  # Reference to MapUI instance

            def send_coordinates(self, lat, lng):
                print(f"Received from HTML: Latitude={lat}, Longitude={lng}")
                self.map_ui.coordinates = (lat, lng)  # Store received coordinates

        api_instance = Api(self)  # Create API instance linked to MapUI
        webview.create_window(
            "Embedded Map",
            str(self.map_html),
            width=800,
            height=600,
            background_color="#19232d",
            js_api=api_instance,  # Attach the JavaScript API
        )
        webview.start()


# Entry point for the webview process
if __name__ == "__main__":
    import argparse

    print(__name__)
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--webview", action="store_true", help="Run webview in a separate process")
    args = parser.parse_args()

    if args.webview:
        # If --webview flag is passed, run the webview window
        # script_path = os.path.abspath(__file__)
        map_ui = MapUI(STATIC_DIR / "map.html")
        map_ui.run_webview()
