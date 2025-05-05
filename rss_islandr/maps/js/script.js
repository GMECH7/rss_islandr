class MapManager {
  constructor() {
    this.map = null;
    this.layers = {};
    this.clickMarker = null;
    this.initMap();
    this.initLayers();
    this.initEventHandlers();
    this.initPyWebViewIntegration();
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
      this.setMarker(e.latlng.lat, e.latlng.lng);
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
    if (window.pywebview?.api) {
      console.log("Sending coordinates to pywebview:", lat, lng);
      window.pywebview.api.send_coordinates(lat, lng);
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
