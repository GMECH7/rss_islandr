class MapManager {
  constructor() {
    this.map = null;
    this.layers = {};
    this.clickMarker = null;
    this.drawnItems = new L.FeatureGroup(); // Store all drawn items
    this.currentDrawingMode = null; // Track current drawing mode
    this.isDrawing = false; // Track if currently drawing
    this.initMap();
    this.initLayers();
    this.initEventHandlers();
    this.initPyWebViewIntegration();
    this.initDrawingControls();

  }

  initMap() {
    this.map = L.map("map").setView(MAP_CONFIG.center, MAP_CONFIG.zoom);

    L.tileLayer(MAP_CONFIG.baseLayer.url, {
      attribution: MAP_CONFIG.baseLayer.attribution,
    }).addTo(this.map);
  }


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
        this.toggleLegend(config.legendId, true);
      }
    });
  }

  initEventHandlers() {
    // Map click handler
    this.map.on("click", (e) => {
      if (e.originalEvent.ctrlKey && !this.isDrawing) { // Only set marker if Ctrl is pressed and not drawing
        this.setMarker(e.latlng.lat, e.latlng.lng);
      }
    });

    // Dynamic checkbox event listeners
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

    // Manual coordinate submission
    document
      .getElementById("updateMarkerBtn")
      ?.addEventListener("click", () => this.updateMarker());

    // Add Enter key listeners for coordinate inputs
    document.getElementById('lat')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.updateMarker();
      }
    });

    document.getElementById('lng')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.updateMarker();
      }
    });

    // Add event listeners for drawing buttons
    document.getElementById('drawSourceBtn')?.addEventListener('click', () => this.startDrawing('source'));
    document.getElementById('drawPathwayBtn')?.addEventListener('click', () => this.startDrawing('pathway'));
    document.getElementById('drawReceiverBtn')?.addEventListener('click', () => this.startDrawing('receiver'));
    document.getElementById('clearDrawingsBtn')?.addEventListener('click', () => this.clearDrawings());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isDrawing) {
        this.cancelDrawing();
      }
    });

  }

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
      case 'receiver':
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

  finalizeDrawing(layer) {
    // Add type metadata to the layer
    layer.feature = layer.feature || {};
    layer.feature.type = 'polygon:' + this.currentType;

    // Get all coordinates as array of [lat, lng] tuples
    const coordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);

    // Store coordinates in layer properties
    layer.feature.properties = {
      coordinates: coordinates,
      area_m2: L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]),
      area_km2: L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]) / 1000000
    };

    // Add to our feature group
    this.drawnItems.addLayer(layer);

    // Create popup content with coordinates
    const popupContent = `
    <b>${this.currentType.toUpperCase()}</b>
    <br>Area: ${layer.feature.properties.area_km2.toFixed(6)} km²
    <br>Nodes: ${coordinates.length}
    <div class="coord-preview" style="max-height: 150px; overflow-y: auto; padding: 5px; background: #f5f5f5; border-radius: 3px; margin-top: 5px;">
        ${coordinates.slice(0, 100).map(coord =>
      `<div style="padding: 2px 0; font-family: monospace;">${coord[0].toFixed(6)}, ${coord[1].toFixed(6)}</div>`
    ).join('')}
        ${coordinates.length > 100 ? '<div style="padding: 2px 0; color: #666;">...and ' + (coordinates.length - 100) + ' more</div>' : ''}
    </div>
`;

    layer.bindPopup(popupContent);

    // Send to backend if needed
    this.sendDrawing(layer);

    // Reset drawing mode
    this.currentDrawingMode = null;
    this.currentType = null;
    this.isDrawing = false;
  }

  sendDrawing(layer) {
    if (window.pywebview?.api) {
      const featureData = {
        type: layer.feature.type,
        coordinates: layer.feature.properties.coordinates,
        area_km2: layer.feature.properties.area_km2,
        node_count: layer.feature.properties.coordinates.length
      };

      console.log("Sending polygon data to pywebview:", featureData);
      window.pywebview.api.send_drawing(featureData);
    }
  }

  clearDrawings() {
    this.drawnItems.clearLayers();
    if (window.pywebview?.api) {
      window.pywebview.api.clear_drawings();
    }
  }

  cancelDrawing() {
    // Cancel drawing by ESC while drawing
    if (this.currentDrawingMode) {
      this.currentDrawingMode.disable();
      this.currentDrawingMode = null;
      this.currentType = null;
      this.isDrawing = false;
    }
  }


  initPyWebViewIntegration() {
    document.addEventListener("pywebviewready", () => {
      console.log("PyWebView is ready!");
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
    });
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
    this.toggleLegend(config.legendId, isActive);
  }

  toggleLegend(legendId, show) {
    const legend = document.getElementById(legendId);
    if (legend) {
      legend.style.display = show ? "block" : "none";
    }
  }

  setMarker(lat, lng) {
    if (this.clickMarker) {
      this.clickMarker.setLatLng([lat, lng]);
    } else {
      this.clickMarker = L.marker([lat, lng]).addTo(this.map);
    }

    this.map.setView([lat, lng]);
    document.getElementById("lat").value = lat.toFixed(5);
    document.getElementById("lng").value = lng.toFixed(5);
    this.sendLocation(lat, lng);
  }

  updateMarker() {
    const latInput = document.getElementById("lat").value.trim();
    const lngInput = document.getElementById("lng").value.trim();

    // Try to parse DMS (Degrees, Minutes, Seconds) format if needed
    const lat = this.parseCoordinate(latInput, true);
    const lng = this.parseCoordinate(lngInput, false);

    if (!isNaN(lat) && !isNaN(lng)) {
      if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        this.setMarker(lat, lng);
      } else {
        alert(
          "Invalid coordinates:\nLatitude must be between -90 and 90\nLongitude must be between -180 and 180"
        );
      }
    } else {
      alert(
        "Please enter valid latitude and longitude in decimal degrees format."
      );
    }
  }
  // Helper method to parse various coordinate formats
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

  sendLocation(lat, lng) {
    // Format coordinates to 4 decimal places
    const formattedLat = parseFloat(lat).toFixed(4);
    const formattedLng = parseFloat(lng).toFixed(4);

    if (window.pywebview?.api) {
      console.log("Sending coordinates to pywebview:", formattedLat, formattedLng);
      window.pywebview.api.send_coordinates(formattedLat, formattedLng);
    } else {
      console.warn("PyWebView API not ready. Skipping coordinate send.");
    }
  }
}

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

// Initialize the map when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.mapManager = new MapManager();
  window.map = window.mapManager.map; // 👈 THIS is the only line you need to add
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
