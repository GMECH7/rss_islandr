// Map Configuration
const MAP_CONFIG = {
    center: [53.3439, 23.0622],
    zoom: 4,
    baseLayer: {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      //attribution: 'Map data © OpenStreetMap contributors'
    }
  };
  
  // WMS Layers Configuration
  const WMS_LAYERS = {
    geology: {
      name: 'Geology',
      url: 'https://geoserver.geo-zs.si/egdi-surface-geology/gsmlp/wms',
      params: {
        layers: 'gsmlp:GeologicUnitView_Lithology',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution: 'Geological Survey of Slovenia (GeoZS)',
      legendId: 'GeologyLegend',
      defaultOn: false
    },
    mines: {
      name: 'Mines',
      url: 'https://data.geus.dk/egdi/wms/',
      params: {
        layers: 'egdi_mines',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution:'<a href="https://maps.europe-geology.eu/?mapname=egdi_geoera_mintell4eu#baslay=baseMapGEUS&extent=302590,950050,8202390,5515330&layers=egdi_mines&filter_0=commodity.part%3D%26status.multi%3D%26miningactivity.multi%3D" target="_blank">Mintell4EU Project</a>',
      legendId: 'MinesLegend',
      defaultOn: false
    },
    hydroEurope: {
      name: 'HydroEurope',
      url: 'https://services.bgr.de/wms/grundwasser/ihme1500/',
      params: {
        layers: '0,1,2',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution: 'BGR & UNESCO (eds.) (2019): International Hydrogeological Map of Europe 1:1,500,000 (IHME1500)',
      legendId: 'HydroEuropeLegend',
      defaultOn: false
    },
    hydroGlobal: {
      name: 'HydroGlobal',
      url: 'https://services.bgr.de/wms/grundwasser/whymap_gwr/',
      params: {
        layers: '0',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution:'BGR: Groundwater Resources of the World (WHYMAP GWR) (WMS)',
      legendId: 'HydroGlobalLegend',
      defaultOn: false
    },
    soilEurope: {
      name: 'SoilEurope',
      url: 'https://services.bgr.de/wms/boden/eusr5000/',
      params: {
        layers: '1,3,5',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution:'BGR: Soil Regions of the European Union and Adjacent Countries 1:5,000,000 (WMS)',
      legendId: 'SoilEuropeLegend',
      defaultOn: false
    },
    riverNetwork: {
      name: 'RiverNetwork',
      url: 'https://image.discomap.eea.europa.eu/arcgis/services/EUHydro/EUHydro_RiverNetworkDatabase/MapServer/WMSServer',
      params: {
        layers: '0,1,2,3,4,5',
        format: 'image/png',
        transparent: true,
        version: '1.3.0'
      },
      attribution: 'Generated using European Union\'s Copernicus Land Monitoring Service information',
      legendId: 'RiverNetworkLegend',
      defaultOn: false
    }
  };
  
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
      this.map = L.map('map').setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
      L.tileLayer(MAP_CONFIG.baseLayer.url, {
        attribution: MAP_CONFIG.baseLayer.attribution
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
      this.map.on('click', (e) => {
        this.setMarker(e.latlng.lat, e.latlng.lng);
      });
  
      // Dynamic checkbox event listeners
      Object.keys(this.layers).forEach(key => {
        const checkbox = document.getElementById(`toggle${key.charAt(0).toUpperCase() + key.slice(1)}`);
        if (checkbox) {
          checkbox.addEventListener('change', () => this.toggleLayer(key, checkbox.checked));
        }
      });
  
      // Manual coordinate submission
      document.getElementById('updateMarkerBtn')?.addEventListener('click', () => this.updateMarker());
    }
  
    initPyWebViewIntegration() {
      document.addEventListener("pywebviewready", () => {
        console.log("PyWebView is ready!");
        // Ensure default layers are toggled on
        Object.entries(this.layers).forEach(([key, { config }]) => {
          const checkbox = document.getElementById(`toggle${key.charAt(0).toUpperCase() + key.slice(1)}`);
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
        legend.style.display = show ? 'block' : 'none';
      }
    }
  
    setMarker(lat, lng) {
      if (this.clickMarker) {
        this.clickMarker.setLatLng([lat, lng]);
      } else {
        this.clickMarker = L.marker([lat, lng]).addTo(this.map);
      }
  
      this.map.setView([lat, lng]);
      document.getElementById('lat').value = lat.toFixed(5);
      document.getElementById('lng').value = lng.toFixed(5);
      this.sendLocation(lat, lng);
    }
  
    updateMarker() {
      const lat = parseFloat(document.getElementById('lat').value);
      const lng = parseFloat(document.getElementById('lng').value);
      if (!isNaN(lat) && !isNaN(lng)) {
        this.setMarker(lat, lng);
      } else {
        alert("Please enter valid latitude and longitude.");
      }
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
    legend.classList.toggle('collapsed');
    button.textContent = legend.classList.contains('collapsed') ? '+' : '–';
}

  document.getElementById('togglePanelBtn').addEventListener('click', function () {
    const panel = document.getElementById('controlsPanel');
    panel.classList.toggle('hidden');
});
  
  // Initialize the map when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    window.mapManager = new MapManager();
  });

  document.addEventListener('DOMContentLoaded', function() {
    const headers = document.querySelectorAll('.map-group-header');
    
    headers.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('.toggle-icon');
            
            // Toggle active class
            content.classList.toggle('active');
            this.classList.toggle('active');
            
            // Update icon
            icon.textContent = content.classList.contains('active') ? '-' : '+';
        });
    });
});