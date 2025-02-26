import os
import subprocess
import sys
from pathlib import Path

CRNT_DIR = Path(__file__).parent
STATIC_DIR = CRNT_DIR.resolve().parent / "static"


class MapUI:
    def __init__(self, map_html: Path):
        self.map_html = map_html
        self.webview_process = None

    def show_map(self):
        """Launch the webview window in a separate process."""
        script_path = os.path.abspath(__file__)  # Path to the current script
        self.webview_process = subprocess.Popen([sys.executable, script_path, "--webview"])

    def close_map(self):
        """Terminate the webview process."""
        if self.webview_process:
            self.webview_process.terminate()
            self.webview_process = None

    def run_webview(self):
        """Run the webview window (to be called in a separate process)."""
        import webview

        webview.create_window(
            "Embedded Map",
            str(self.map_html),
            width=800,
            height=600,
            background_color="#19232d",
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
