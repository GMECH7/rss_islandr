import contextlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from tkinter import messagebox

import ttkbootstrap as tb
import webview

from rss_islandr.core.datatypes import PolygonDataDict
from rss_islandr.core.helpers import extract_dicts_from_string
from rss_islandr.core.logger_config import logger_decorator

logger = logging.getLogger(__name__)

if sys.platform.startswith("linux"):
    # GTK is tried first by default and logs a (harmless) error when PyGObject is missing. Qt is the backend we install.
    os.environ.setdefault("PYWEBVIEW_GUI", "qt")

#: Code run by the map process. `-c` is used instead of `-m` because the package imports this module,
#: and `-m` would execute it a second time (RuntimeWarning).
MAP_PROCESS_CODE = "from rss_islandr.ui.map_ui import _run_map_process; _run_map_process()"


class Api:
    def __init__(self, map_ui_instance):
        self.map_ui = map_ui_instance

    @logger_decorator
    def py_api_coord_receiver(self, lat: float, lng: float, crs: str):
        """Receive coordinates from JavaScript"""
        self.map_ui.coordinates = (lat, lng, crs)  # Store received coordinates
        logger.debug(f"Received coordinates: Latitude={lat}, Longitude={lng}, CRS={crs}")

    @logger_decorator
    def py_api_polygons_receiver(self, polygon_data: PolygonDataDict):
        """
        Receive polygon data from JavaScript.
        """
        logger.debug(f"Received polygon data: {polygon_data}")

        # Ensure unique_id exists
        if "unique_id" not in polygon_data:
            logger.error("Received polygon without unique_id!")
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
            logger.debug(f"Updated existing polygon: {polygon}")
        else:
            # Add new polygon
            self.map_ui.polygons.append(polygon)
            logger.debug(f"Added new polygon: {polygon}")

        self.map_ui.map_polygons_tb.set(f"{self.map_ui.polygons}")
        return True

    @logger_decorator
    def py_api_clear_polygons(self):
        """Clear all stored polygons"""
        logger.debug("Clearing all polygons from storage")
        self.map_ui.polygons = []  # Empty the list
        self.map_ui.map_polygons_tb.set("")  # Clear the StringVar
        return True

    @logger_decorator
    def py_api_delete_polygons(self, polygon_data: PolygonDataDict):
        """Delete a polygon from storage based on its unique_id and type"""
        logger.debug(f"Deleting polygon: {polygon_data}")

        # Keep polygons that do not match the given polygon_data
        self.map_ui.polygons = [
            poly
            for poly in self.map_ui.polygons
            if not (poly["name"] == polygon_data["name"] and poly["type"] == polygon_data["type"])
        ]

        logger.debug(f"Remaining polygons: {len(self.map_ui.polygons)}")
        return True

    @logger_decorator
    def py_api_send_polygons_to_js(self):
        """Return all stored polygons to JavaScript for redrawing"""
        logger.debug(f"Polygons sent to js: {self.map_ui.polygons}")
        return self.map_ui.polygons

    @logger_decorator
    def py_api_send_coordinates_to_js(self) -> tuple[float | None, float | None, str]:
        """Return the latest coordinates to JavaScript"""
        logger.debug(f"Coordinates sent to JavaScript: {self.map_ui.lat}, {self.map_ui.lng}")
        if self.map_ui.lat is None or self.map_ui.lat == "":
            self.map_ui.lat = None
        else:
            self.map_ui.lat = float(self.map_ui.lat)

        if self.map_ui.lng is None or self.map_ui.lng == "":
            self.map_ui.lng = None
        else:
            self.map_ui.lng = float(self.map_ui.lng)

        return self.map_ui.lat, self.map_ui.lng, self.map_ui.crs


class _ChildMapState:
    """
    State of the map when it runs in its own process (Linux/macOS).

    It offers the attributes that `Api` uses on `MapUI` and saves them to a JSON file on every change,
    so that the main app gets the work done in the map even if the map process crashes.
    """

    class _PolygonsText:
        def __init__(self, owner: "_ChildMapState"):
            self.__owner = owner

        def set(self, _value: str) -> None:
            self.__owner.flush()

    def __init__(self, payload: dict):
        self.__result_file = payload["result_file"]
        self.__polygons = payload["polygons"]
        self.__coordinates = None
        self.lat = payload["lat"]
        self.lng = payload["lng"]
        self.crs = payload["crs"]
        self.map_polygons_tb = self._PolygonsText(self)

    @property
    def polygons(self) -> list:
        return self.__polygons

    @polygons.setter
    def polygons(self, value: list) -> None:
        self.__polygons = value
        self.flush()

    @property
    def coordinates(self):
        return self.__coordinates

    @coordinates.setter
    def coordinates(self, value) -> None:
        self.__coordinates = value
        self.flush()

    def flush(self) -> None:
        tmp_file = f"{self.__result_file}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as file_out:
            json.dump({"polygons": self.__polygons, "coordinates": self.__coordinates}, file_out)
        os.replace(tmp_file, self.__result_file)


def _run_map_process() -> None:
    """Entry point of the map process: read the initial state from stdin, show the map, save changes to a file."""
    payload = json.load(sys.stdin)
    state = _ChildMapState(payload)
    state.flush()
    webview.create_window(
        "Maps Viewer",
        payload["map_html"],
        width=1600,
        height=900,
        background_color=payload["background_color"],
        js_api=Api(state),
    )
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.start(debug=False)


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
        self.crs = None

    @logger_decorator
    def update_coordinates(self):
        """
        Update coordinates (self.coordinates) from StringVar content.

        This methood is called in the following cases:
        1. When a scenario is imported.
        2. When restoring defaults in the main app UI.
        """
        self.crs = self.ui_inp_vars.get("map_0_00").tk_var.get()
        self.lat = self.ui_inp_vars.get("map_0_01").tk_var.get()
        self.lng = self.ui_inp_vars.get("map_0_02").tk_var.get()

    @logger_decorator
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
            logger.debug(f"Updated polygons from import: {self.polygons}")
        except Exception as e:
            logger.error(f"Error parsing polygons from StringVar: {e}")

    @logger_decorator
    def show_map(self):
        """Launch the webview window in a separate process."""
        self.webview_process = subprocess.Popen([sys.executable, __file__, "--webview"])

    @logger_decorator
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

    @logger_decorator
    def run_webview(self):
        """
        Show the map and block until the map window is closed.

        On Windows the map runs in this process. Elsewhere it runs in its own process, because the Qt/Cocoa
        web engines cannot be started twice in the same process and a crash of the engine would close the app.
        """
        if sys.platform == "win32":
            self.__run_webview_in_process()
        else:
            self.__run_webview_in_subprocess()

    def __run_webview_in_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result_file = Path(tmp_dir) / "map_state.json"
            payload = {
                "map_html": str(self.map_html),
                "background_color": self.__style.colors.bg,  # type: ignore
                "polygons": self.polygons,
                "lat": self.lat,
                "lng": self.lng,
                "crs": self.crs,
                "result_file": str(result_file),
            }
            project_dir = Path(__file__).resolve().parents[2]
            try:
                completed = subprocess.run(
                    self.__map_process_command(),
                    input=json.dumps(payload),
                    text=True,
                    cwd=project_dir,
                )
                if completed.returncode != 0:
                    logger.error(f"Map process ended with return code {completed.returncode}")
            except Exception as e:
                logger.error(f"Could not start the map process: {e}")
                messagebox.showerror("Map Error", f"Could not load the map component.\n\nError: {e}")
                return

            self.__read_map_state(result_file)

    @staticmethod
    def __map_process_command() -> list[str]:
        if getattr(sys, "frozen", False):  # Packaged app: sys.executable is the app itself
            return [sys.executable, "--map-process"]
        return [sys.executable, "-c", MAP_PROCESS_CODE]

    def __read_map_state(self, result_file: Path) -> None:
        """Take over the polygons and coordinates saved by the map process."""
        try:
            with open(result_file, "r", encoding="utf-8") as file_inp:
                state = json.load(file_inp)
        except (OSError, ValueError) as e:
            logger.error(f"Could not read the state of the map process: {e}")
            return

        self.polygons = state["polygons"]
        self.map_polygons_tb.set(f"{self.polygons}" if self.polygons else "")
        coordinates = state["coordinates"]
        if coordinates is not None:
            self.coordinates = tuple(coordinates)

    def __run_webview_in_process(self) -> None:
        """Run the webview window in this process (blocks until it is closed)."""
        api_instance = Api(self)  # Create API instance linked to MapUI
        try:
            webview.create_window(
                "Maps Viewer",
                str(self.map_html),
                width=1600,
                height=900,
                background_color=self.__style.colors.bg,  # type: ignore
                js_api=api_instance,  # Attach the JavaScript API
            )

            logger.debug("Webview started. Waiting for coordinates...")
            # Set the webview settings to avoid opening devtools when debugging is True
            webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
            webview.settings["ALLOW_DOWNLOADS"] = True
            webview.start(debug=False)
        except Exception as e:
            msg = f"Could not load the map component. Please contact support.\n\nError: {e}"
            messagebox.showerror("Map Error", msg)
