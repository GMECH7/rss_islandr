/**
 * Manages a Leaflet map with layers, drawing tools, and event handlers.
 * @class
 */
class MapManager {
  constructor() {
    this.map = null;
    this.layers = {};
    this.clickMarker = null; //Store a marker when clicking on map
    this.drawnItems = new L.FeatureGroup(); // Store all drawn items (Leaflet)
    this.currentDrawingMode = null; // Track current drawing mode
    this.isDrawing = false; // Track if drawing is in progress

    // Define CRS and get selector element
    this.crsSelector = document.getElementById('crs-select');
    proj4.defs('EPSG:2100', '+proj=tmerc +lat_0=0 +lon_0=24 +k=0.9996 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=-199.87,74.79,246.62,0,0,0,0 +units=m +no_defs');

    // initialization methods
    this.initMap();
    this.initLayers();
    this.initEventHandlers();
    this.initPyWebViewIntegration();
    this.initDrawingControls();
  }

  /**
   * Initializes the Leaflet map with a base tile layer and default view.
   * 
   * MAP_CONFIG from config.js is used
   */
  initMap() {
    this.map = L.map("map").setView(MAP_CONFIG.center, MAP_CONFIG.zoom);

    L.tileLayer(MAP_CONFIG.baseLayer.url, {
      attribution: MAP_CONFIG.baseLayer.attribution,
    }).addTo(this.map);
  }

  /**
   * Initializes WMS layers and adds them to the map.
   * 
   * WMS_LAYERS from config.js is used
   */
  initLayers() {
    Object.entries(WMS_LAYERS).forEach(([key, config]) => {
      const layer = L.tileLayer.wms(config.url, config.params);
      if (config.attribution) {
        layer.options.attribution = config.attribution;
      }
      this.layers[key] = { layer, config };

      // Initialize default layers
      if (config.defaultOn) {
        layer.addTo(this.map);
        this.visibilityLegend(config.legendId, true);
      }
    });
  }

  initEventHandlers() {
    // Set map marker if pressing Ctrl + Left click and not drawing
    this.map.on("click", (e) => {
      if (e.originalEvent.ctrlKey && !this.isDrawing) {
        if (this.clickMarker && this.map.hasLayer(this.clickMarker)) {
          this.deleteMarker();
        } else {
          this.setMarker(e.latlng.lat, e.latlng.lng, true);
        }
      }
    });

    // Set dynamic checkboxes
    Object.keys(this.layers).forEach((key) => {
      const checkbox = document.getElementById(
        `toggle${key.charAt(0).toUpperCase() + key.slice(1)}`
      );
      if (checkbox) {
        checkbox.addEventListener("change", () =>
          this.toggleLayer(key, checkbox.checked)
        );
      }
    });

    // Update lat-long coordinates after placing marker 
    document
      .getElementById("updateMarkerBtn")
      ?.addEventListener("click", () => this.updateMarker());

    // Update longtitude after typing it in the respective entry box by pressing Enter
    document.getElementById('lat')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.updateMarker();
      }
    });

    // Update longtitude after typing it in the respective entry box by pressing Enter
    document.getElementById('lng')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.updateMarker();
      }
    });

    // Event listeners for drawing buttons
    document.getElementById('drawSourceBtn')?.addEventListener('click', () => this.startDrawing('source'));
    document.getElementById('drawPathwayBtn')?.addEventListener('click', () => this.startDrawing('pathway'));
    document.getElementById('drawReceptorBtn')?.addEventListener('click', () => this.startDrawing('receptor'));
    document.getElementById('clearDrawingsBtn')?.addEventListener('click', () => this.clearDrawings());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isDrawing) {
        this.cancelDrawing();
      }
    });

    // Add event listener for the CRS dropdown
    this.crsSelector.addEventListener('change', () => this.updateCoordinateDisplay());
  }

  initPyWebViewIntegration() {
    const tryInit = () => {
      if (window.pywebview?.api) {
        console.log("✅ PyWebView is ready!");
        this.handlePyWebViewReady();
        this.initializeFromBackend();
      } else {
        console.log("⏳ Waiting for PyWebView...");
        setTimeout(tryInit, 300); // Retry every 300ms
      }
    };

    tryInit(); // Start checking immediately
  }

  // HELPER METHOD: Updates the coordinate input fields based on the current marker and selected CRS.
  updateCoordinateDisplay() {
    if (!this.clickMarker) return; // Exit if no marker is set

    const lat = this.clickMarker.getLatLng().lat;
    const lng = this.clickMarker.getLatLng().lng;
    const selectedCRS = this.crsSelector.value;
    const latInput = document.getElementById('lat');
    const lngInput = document.getElementById('lng');

    if (selectedCRS === 'EPSG:4326') {
      latInput.value = lat.toFixed(6);
      lngInput.value = lng.toFixed(6);
      latInput.placeholder = "Latitude";
      lngInput.placeholder = "Longitude";
    } else {
      const converted = proj4('EPSG:4326', selectedCRS, [lng, lat]);
      latInput.value = converted[0].toFixed(2); // This is now X
      lngInput.value = converted[1].toFixed(2); // This is now Y
      latInput.placeholder = "X Coordinate";
      lngInput.placeholder = "Y Coordinate";
    }
  }

  handlePyWebViewReady() {
    console.log("PyWebView is confirmed ready!");

    if (window.pywebview?.api) {
      console.log("API available, requesting polygons...");
      window.pywebview.api.py_api_send_polygons_to_js().then(polygons => {
        if (polygons && polygons.length > 0) {
          console.log(`Received ${polygons.length} polygons to redraw`);
          this.redrawPolygons(polygons);
        }
      });
    }
    // Ensure default layers are toggled on
    Object.entries(this.layers).forEach(([key, { config }]) => {
      const checkbox = document.getElementById(
        `toggle${key.charAt(0).toUpperCase() + key.slice(1)}`
      );
      if (checkbox) {
        checkbox.checked = config.defaultOn; // Set checkbox checked based on defaultOn value
        // If the checkbox is checked, add the layer
        if (checkbox.checked) {
          this.toggleLayer(key, true); // Call toggleLayer to ensure the layer is added
        }
      }
    });
  }

  /**
   * Initializes the Leaflet.draw control with custom settings:
   * - Drawing tools are hidden (managed by custom buttons).
   * - All drawings are stored in `this.drawnItems`.
   * - Triggers `finalizeDrawing()` on shape completion.
  */
  initDrawingControls() {
    // Add the feature group to the map
    this.drawnItems.addTo(this.map);

    // Initialize the draw control
    this.drawControl = new L.Control.Draw({
      position: 'bottomleft',
      edit: {
        featureGroup: this.drawnItems
      },
      draw: {
        polygon: false,
        rectangle: false,
        circle: false,
        marker: false,
        polyline: false,
        circlemarker: false
      }
    });

    this.drawControl.addTo(this.map);

    // Listen for drawing events
    this.map.on(L.Draw.Event.CREATED, (e) => {
      const layer = e.layer;
      this.finalizeDrawing(layer);
    });

    // Listen for edit events
    this.map.on(L.Draw.Event.EDITED, (e) => {
      const layers = e.layers;
      layers.eachLayer((layer) => {
        // Update geometry and metadata
        const coords = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
        const area_m2 = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);

        layer.feature.properties.coordinates = coords;
        layer.feature.properties.area_m2 = area_m2;
        layer.feature.properties.area_km2 = area_m2 / 1_000_000;
        layer.feature.properties.node_count = coords.length;

        // 🔥 Update popup content immediately after editing
        layer.setPopupContent(this.createPopupContent(layer));

        // Rebind rename handler (optional but good practice)
        layer.off('popupopen'); // remove old handler if any
        layer.on('popupopen', () => {
          document.querySelector('.rename-btn')?.addEventListener('click', () => {
            const newName = prompt("Enter new name:", layer.feature.properties.name);
            if (newName) {
              layer.feature.properties.name = newName;
              layer.setPopupContent(this.createPopupContent(layer));
              this.sendDrawing(layer);
            }
          });
        });

        // Send updated data to Python backend
        this.sendDrawing(layer);
      });
    });


    // Listen for delete events
    this.map.on(L.Draw.Event.DELETED, (e) => {
      const layers = e.layers;
      layers.eachLayer((layer) => {
        if (window.pywebview?.api && layer.feature) {
          window.pywebview.api.py_api_delete_polygons({
            type: layer.feature.type,
            name: layer.feature.properties.name
          });
        }
      });
    });
  }


  async initializeFromBackend() {
    if (!window.pywebview?.api) {
      console.warn("PyWebView API not available when trying to initialize coordinates");
      return;
    }

    try {
      // Expecting [coord1, coord2, crs] from your Python function
      const [coord1, coord2, crs] = await window.pywebview.api.py_api_send_coordinates_to_js();
      console.log(`Received initial state: ${coord1}, ${coord2} in ${crs}`);

      // Exit if the data is invalid or represents a default (0,0) state
      if (!crs || (parseFloat(coord1) === 0 && parseFloat(coord2) === 0)) {
        return;
      }

      // --- This is the new, important logic ---

      // 1. Set the CRS dropdown to match the loaded value.
      this.crsSelector.value = crs;

      let lat, lng;

      // 2. Convert the coordinates to WGS84 Lat/Lon for Leaflet, if necessary.
      if (crs === 'EPSG:4326') {
        // If the CRS is WGS84, the values are already lat and lon.
        lat = parseFloat(coord1);
        lng = parseFloat(coord2);
      } else {
        // If it's a projected CRS (like GGRS87), convert X/Y back to Lat/Lon.
        const x = parseFloat(coord1);
        const y = parseFloat(coord2);
        const converted = proj4(crs, 'EPSG:4326', [x, y]); // Inverse projection
        lng = converted[0];
        lat = converted[1];
      }

      // 3. Call setMarker with the guaranteed WGS84 coordinates.
      if (!isNaN(lat) && !isNaN(lng)) {
        // The `false` flag prevents sending the data back to Python in a loop.
        this.setMarker(lat, lng, false);
      }

    } catch (error) {
      console.error("Error getting initial coordinates:", error);
    }
  }

  startDrawing(type) {
    if (!L.Draw || !L.Draw.Polygon) {
      alert('Drawing functionality not available. Please ensure Leaflet.draw plugin is loaded.');
      return;
    }
    this.isDrawing = true;
    // Disable any current drawing mode
    if (this.currentDrawingMode) {
      this.currentDrawingMode.disable();
    }

    // Set style based on type
    let style = {};
    switch (type) {
      case 'source':
        style = { color: '#ff0000', fillColor: '#ff0000', fillOpacity: 0.01 };
        break;
      case 'pathway':
        style = { color: '#0000ff', fillColor: '#0000ff', fillOpacity: 0.01, dashArray: '5,5' };
        break;
      case 'receptor':
        style = { color: '#00aa00', fillColor: '#00aa00', fillOpacity: 0.01 };
        break;
    }

    // Initialize the appropriate drawing tool
    this.currentDrawingMode = new L.Draw.Polygon(this.map, {
      shapeOptions: style,
      showArea: true,
      metric: true,
      guideLayers: this.drawnItems,
    });

    this.currentDrawingMode.enable();
    this.currentType = type; // Store the current type for finalization
  }

  /**
 * Generates a unique ID for polygons
 * @returns {string} Unique ID
 */
  generatePolygonId() {
    return 'polygon_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  finalizeDrawing(layer) {
    // Prompt user for polygon name
    const defaultName = `${this.currentType.charAt(0).toUpperCase() + this.currentType.slice(1)}`;
    const polygonName = prompt("Enter polygon name:", defaultName) || defaultName;

    // Add type metadata to the layer
    layer.feature = layer.feature || {};
    layer.feature.type = 'polygon:' + this.currentType;

    // Generate and assign unique ID
    const uniqueId = this.generatePolygonId();
    layer.feature.unique_id = uniqueId;

    // Get all coordinates as array of [lat, lng] tuples
    const coordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);

    // Store coordinates and name in layer properties
    layer.feature.properties = {
      name: polygonName,
      coordinates: coordinates,
      area_m2: L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]),
      area_km2: L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]) / 1000000,
      node_count: coordinates.length,
      unique_id: uniqueId  // Store in properties too for consistency
    };

    // Add to our feature group
    this.drawnItems.addLayer(layer);

    // Create enhanced popup content
    layer.bindPopup(this.createPopupContent(layer));

    // Setup rename handler
    layer.on('popupopen', () => {
      document.querySelector('.rename-btn')?.addEventListener('click', () => {
        const newName = prompt("Enter new name:", layer.feature.properties.name);
        if (newName) {
          layer.feature.properties.name = newName;
          layer.setPopupContent(this.createPopupContent(layer));
          this.sendDrawing(layer);
        }
      });
    });

    // Send to backend
    this.sendDrawing(layer);

    // Reset drawing mode
    this.currentDrawingMode = null;
    this.currentType = null;
    this.isDrawing = false;
  }

  // Helper method to create popup content (extracted for reuse)
  createPopupContent(layer) {
    return `
    <div style="min-width: 200px;">
      <b>${layer.feature.properties.name}</b>
      <div style="color: #666; font-size: 0.9em; margin-bottom: 8px;">${layer.feature.type.split(':')[1].toUpperCase()}</div>
      <div>Area: ${layer.feature.properties.area_km2.toFixed(6)} km²</div>
      <div>Nodes: ${layer.feature.properties.coordinates.length}</div>
      <button class="rename-btn" style="margin-top: 8px; padding: 2px 6px; font-size: 0.8em;">
        Rename
      </button>
      <div style="margin-top: 10px; max-height: 150px; overflow-y: auto;">
        <table style="width: 100%; border-collapse: collapse; font-family: monospace; font-size: 0.9em;">
          <thead>
            <tr style="background-color: #f0f0f0;">
              <th style="padding: 4px; text-align: left; border-bottom: 1px solid #ddd;">Latitude</th>
              <th style="padding: 4px; text-align: left; border-bottom: 1px solid #ddd;">Longitude</th>
            </tr>
          </thead>
          <tbody>
            ${layer.feature.properties.coordinates.slice(0, 100).map(coord =>
      `<tr>
                <td style="padding: 4px; border-bottom: 1px solid #eee;">${coord[0].toFixed(6)}</td>
                <td style="padding: 4px; border-bottom: 1px solid #eee;">${coord[1].toFixed(6)}</td>
              </tr>`
    ).join('')}
            ${layer.feature.properties.coordinates.length > 100 ?
        `<tr>
                <td colspan="2" style="padding: 4px; text-align: center; color: #666; font-style: italic;">
                  ...and ${layer.feature.properties.coordinates.length - 100} more
                </td>
              </tr>` : ''}
          </tbody>
        </table>
      </div>
    </div>`;
  }

  /**
   * send drawing to pywebview.
   * @param {*} layer 
   */
  sendDrawing(layer) {
    if (window.pywebview?.api) {
      const polygonDataToPy = {
        unique_id: layer.feature.unique_id,
        type: layer.feature.type,
        name: layer.feature.properties.name,
        coordinates: layer.feature.properties.coordinates,
        area_km2: layer.feature.properties.area_km2,
        node_count: layer.feature.properties.coordinates.length
      };

      console.log("Sending polygon data to pywebview:", polygonDataToPy);
      window.pywebview.api.py_api_polygons_receiver(polygonDataToPy);
    }
  }

  /**
   * Clear all drawings. Button handles that
   */
  clearDrawings() {
    // Clear from the map
    this.drawnItems.clearLayers();

    // Clear from backend storage
    if (window.pywebview?.api) {
      window.pywebview.api.py_api_clear_polygons().then(success => {
        if (success) {
          console.log("All drawings cleared from backend");
        }
      }).catch(error => {
        console.error("Error clearing drawings:", error);
      });
    }
  }

  /**
   * Cancel drawing by ESC while drawing
   */
  cancelDrawing() {
    if (this.currentDrawingMode) {
      this.currentDrawingMode.disable();
      this.currentDrawingMode = null;
      this.currentType = null;
      this.isDrawing = false;
    }
  }

  /**
   * Redraws all polygons from stored data
   * @param {Array} polygons - Array of polygon data objects
   */
  redrawPolygons(polygons) {
    // Clear existing drawings first
    this.drawnItems.clearLayers();

    // Redraw each polygon
    polygons.forEach(polygonData => {
      // Create a new polygon layer
      const polygon = L.polygon(polygonData.coordinates, {
        color: this.getColorForType(polygonData.type),
        fillColor: this.getColorForType(polygonData.type),
        fillOpacity: 0.01,
        dashArray: polygonData.type.includes('pathway') ? '5,5' : undefined
      });

      // Add all original metadata to the layer
      polygon.feature = {
        unique_id: polygonData.unique_id,
        type: polygonData.type,
        properties: {
          ...polygonData,
          coordinates: polygonData.coordinates
        }
      };

      // Add to feature group
      this.drawnItems.addLayer(polygon);

      // Bind popup with working rename functionality
      polygon.bindPopup(this.createPopupContent(polygon));

      // Reattach rename event handler
      polygon.on('popupopen', () => {
        document.querySelector('.rename-btn')?.addEventListener('click', () => {
          const newName = prompt("Enter new name:", polygon.feature.properties.name);
          if (newName) {
            polygon.feature.properties.name = newName;
            polygon.setPopupContent(this.createPopupContent(polygon));
            this.sendDrawing(polygon);
          }
        });
      });
    });
  }

  /**
   * Helper method to get color based on polygon type
   */
  getColorForType(type) {
    if (type.includes('source')) return '#ff0000';
    if (type.includes('pathway')) return '#0000ff';
    if (type.includes('receptor')) return '#00aa00';
    return '#333333'; // default color
  }

  toggleLayer(layerKey, isActive) {
    const { layer, config } = this.layers[layerKey];

    if (isActive) {
      // Add the layer to the map if it's active (checkbox checked)
      if (!this.map.hasLayer(layer)) {
        layer.addTo(this.map);
      }
    } else {
      // Remove the layer from the map if it's inactive (checkbox unchecked)
      if (this.map.hasLayer(layer)) {
        this.map.removeLayer(layer);
      }
    }

    // Toggle the legend visibility based on whether the layer is active
    this.visibilityLegend(config.legendId, isActive);
  }

  visibilityLegend(legendId, show) {
    const legend = document.getElementById(legendId);
    if (legend) {
      legend.style.display = show ? "block" : "none";
    }
  }

  // ✅ MODIFIED: setMarker now uses the helper function to display coordinates.
  setMarker(lat, lng, shouldSendToBackend = true) {

    console.log(`Setting marker at: ${lat}, ${lng} ${typeof lat} ${typeof lng}`); if ((lat === null || lat === '') && (lng === null || lng === '')) {
      if (this.clickMarker) {
        this.map.removeLayer(this.clickMarker);
        this.clickMarker = null;
      }
      return;
    }
    console.log("lelos kanelos")
    if (this.clickMarker) {
      this.clickMarker.setLatLng([lat, lng]);
    } else {
      this.clickMarker = L.marker([lat, lng]).addTo(this.map);
    }

    this.map.setView([lat, lng]);

    // Update UI display based on current dropdown selection
    this.updateCoordinateDisplay();

    if (shouldSendToBackend) {
      const selectedCRS = this.crsSelector.value;

      if (selectedCRS === 'EPSG:4326') {
        // If WGS84, send the original lat/lng
        this.sendLocation(lat, lng, selectedCRS);
      } else {
        // If another CRS, convert first, then send
        const converted = proj4('EPSG:4326', selectedCRS, [lng, lat]);
        const x = converted[0];
        const y = converted[1];
        this.sendLocation(x, y, selectedCRS);
      }
    }
  }

  // updateMarker now performs inverse projection when reading from inputs.
  updateMarker() {
    const latInput = document.getElementById("lat").value.trim(); // This input could be Latitude or X
    const lngInput = document.getElementById("lng").value.trim(); // This input could be Longitude or Y
    const selectedCRS = this.crsSelector.value;
    let lat, lng;

    try {
      if (selectedCRS === 'EPSG:4326') {
        // Original logic for parsing Lat/Lon or DMS
        lat = this.parseCoordinate(latInput, true);
        lng = this.parseCoordinate(lngInput, false);
      } else {
        // New logic for projected coordinates (e.g., GGRS87)
        const x = parseFloat(latInput);
        const y = parseFloat(lngInput);

        if (isNaN(x) || isNaN(y)) {
          throw new Error("Please enter valid numeric X and Y coordinates.");
        }

        // Convert from the selected CRS back to WGS84
        const converted = proj4(selectedCRS, 'EPSG:4326', [x, y]);
        lng = converted[0];
        lat = converted[1];
      }

      if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        throw new Error("Coordinates are invalid or out of bounds.");
      }

      this.setMarker(lat, lng, true);

    } catch (error) {
      alert(error.message);
    }
  }

  deleteMarker() {
    if (this.clickMarker) {
      this.map.removeLayer(this.clickMarker);
      this.clickMarker = null;
    }

    // Clear the input fields
    document.getElementById("lat").value = "";
    document.getElementById("lng").value = "";

    // send default coordinates to frontend
    this.sendLocation(0.0, 0.0);
  }

  /**
   * Helper method to parse various coordinate formats
   * @param {*} input 
   * @param {*} isLatitude 
   * @returns 
   */
  parseCoordinate(input, isLatitude) {
    // Try simple decimal format first
    if (/^-?\d+(\.\d+)?$/.test(input)) {
      return parseFloat(input);
    }

    // Try DMS format (e.g., 40°26'46"N or 40 26 46 N)
    const dmsRegex =
      /([0-9]{1,3})[°\s]?\s?([0-9]{1,2})[′\s']?\s?([0-9]{1,2}(?:\.\d+)?)[″\s"]?\s?([NSEW]?)/i;
    const match = input.match(dmsRegex);

    if (match) {
      const degrees = parseFloat(match[1]);
      const minutes = parseFloat(match[2]) || 0;
      const seconds = parseFloat(match[3]) || 0;
      const direction = match[4].toUpperCase();

      let decimal = degrees + minutes / 60 + seconds / 3600;

      if (direction === "S" || direction === "W") {
        decimal = -decimal;
      }

      // Additional validation for latitude/longitude ranges
      if (isLatitude && Math.abs(decimal) > 90) {
        return NaN;
      }
      if (!isLatitude && Math.abs(decimal) > 180) {
        return NaN;
      }

      return decimal;
    }

    return NaN;
  }

  sendLocation(coord1, coord2, crs) {
    // Format coordinates to 4 decimal places
    const formattedCoord1 = parseFloat(coord1).toFixed(4);
    const formattedCoord2 = parseFloat(coord2).toFixed(4);

    if (window.pywebview?.api) {
      console.log(`Sending coordinates to Python: ${formattedCoord1}, ${formattedCoord2} (${crs})`);

      // Pass all three pieces of information to the Python API
      window.pywebview.api.py_api_coord_receiver(formattedCoord1, formattedCoord2, crs);
    }
  }
}

// TODO This will have to be incorporated in the class
function toggleLegend(button) {
  const legend = button.parentElement;
  legend.classList.toggle("collapsed");
  button.textContent = legend.classList.contains("collapsed") ? "+" : "–";
}

document
  .getElementById("togglePanelBtn")
  .addEventListener("click", function () {
    const panel = document.getElementById("controlsPanel");
    panel.classList.toggle("hidden");
  });

document.addEventListener("DOMContentLoaded", function () {
  const headers = document.querySelectorAll(".map-group-header");

  headers.forEach((header) => {
    header.addEventListener("click", function () {
      const content = this.nextElementSibling;
      const icon = this.querySelector(".toggle-icon");

      // Toggle active class
      content.classList.toggle("active");
      this.classList.toggle("active");

      // Update icon
      icon.textContent = content.classList.contains("active") ? "-" : "+";
    });
  });
});

document.getElementById('captureScreenBtn').addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
    const track = stream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(track);

    const bitmap = await imageCapture.grabFrame();
    const canvas = document.getElementById('screenshotCanvas');
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    canvas.style.display = 'block';
    const ctx = canvas.getContext('2d');
    ctx.drawImage(bitmap, 0, 0);
    track.stop(); // stop screen capture

    // Optional: Save the screenshot as PNG
    const imgURL = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = imgURL;
    a.download = "screenshot.png";
    a.click();

  } catch (err) {
    console.error("Error capturing screen:", err);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  window.mapManager = new MapManager();
  window.map = window.mapManager.map;

  // Check for saved polygons
  if (window.pywebview?.api) {
    window.pywebview.api.py_api_send_polygons_to_js().then(polygons => {
      if (polygons && polygons.length > 0) {
        window.mapManager.redrawPolygons(polygons);
      }
    });
  }
});