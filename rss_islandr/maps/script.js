// Initialize map
var map = L.map('map').setView([53.3439, 23.0622], 4);

// Add base tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data © OpenStreetMap contributors'
}).addTo(map);

// Define WMS layers
var wmsGeologyLayer = L.tileLayer.wms('https://geoserver.geo-zs.si/egdi-surface-geology/gsmlp/wms', {
    layers: 'gsmlp:GeologicUnitView_Lithology',
    format: 'image/png',
    transparent: true,
    version: '1.3.0'
});

var wmsMinesLayer = L.tileLayer.wms('https://data.geus.dk/egdi/wms/', {
    layers: 'egdi_mines',
    format: 'image/png',
    transparent: true,
    version: '1.1.1'
});

var wmsHydroEuropeLayer = L.tileLayer.wms('https://services.bgr.de/wms/grundwasser/ihme1500/', {
    layers: '0,1,2',
    format: 'image/png',
    transparent: true,
    version: '1.3.0'
});

var wmsHydroGlobalLayer = L.tileLayer.wms('https://services.bgr.de/wms/grundwasser/whymap_gwr/', {
    layers: '0',
    format: 'image/png',
    transparent: true,
    version: '1.3.0'
});

var wmsSoilEuropeLayer = L.tileLayer.wms('https://services.bgr.de/wms/boden/eusr5000/', {
    layers: '0,1,2',
    format: 'image/png',
    transparent: true,
    version: '1.3.0'
});


wmsEUHydroRiverLayer = L.tileLayer.wms('https://image.discomap.eea.europa.eu/arcgis/services/EUHydro/EUHydro_RiverNetworkDatabase/MapServer/WMSServer?', {
    layers: '0',
    format: 'image/png',
    transparent: true,
    version: '1.3.0',
    attribution: 'EEA EUHydro River Network'
});

// Handle toggle layer
function toggleLayer(checkbox, layer) {
    if (checkbox.checked) {
        layer.addTo(map);
        if (layer === wmsGeologyLayer) {
            document.getElementById('geologyLegend').style.display = 'block';
        } else if (layer === wmsMinesLayer) {
            document.getElementById('minesLegend').style.display = 'block';
        } else if (layer === wmsHydroEuropeLayer) {
            document.getElementById('hydroLegend').style.display = 'block';
        } else if (layer === wmsHydroGlobalLayer) {
            document.getElementById('hydroLegendGlobal').style.display = 'block';
        } else if (layer === wmsSoilEuropeLayer) {
            document.getElementById('soilLegendEurope').style.display = 'block';
        } else if (layer === wmsEUHydroRiverLayer) {
            document.getElementById('soilLegendEurope').style.display = 'block';
        }
    } else {
        map.removeLayer(layer);
        if (layer === wmsGeologyLayer) {
            document.getElementById('geologyLegend').style.display = 'none';
        } else if (layer === wmsMinesLayer) {
            document.getElementById('minesLegend').style.display = 'none';
        } else if (layer === wmsHydroEuropeLayer) {
            document.getElementById('hydroLegend').style.display = 'none';
        } else if (layer === wmsHydroGlobalLayer) {
            document.getElementById('hydroLegendGlobal').style.display = 'none';
        } else if (layer === wmsSoilEuropeLayer) {
            document.getElementById('soilLegendEurope').style.display = 'none';
        } else if (layer === wmsEUHydroRiverLayer) {
            document.getElementById('soilLegendEurope').style.display = 'none';
        }
    }
}

var clickMarker = null;

function setMarker(lat, lng) {
    if (clickMarker) {
        clickMarker.setLatLng([lat, lng]);
    } else {
        clickMarker = L.marker([lat, lng]).addTo(map);
    }

    map.setView([lat, lng]);
    document.getElementById('lat').value = lat.toFixed(5);
    document.getElementById('lng').value = lng.toFixed(5);
    sendLocation(lat, lng);
}

function updateMarker() {
    var lat = parseFloat(document.getElementById('lat').value);
    var lng = parseFloat(document.getElementById('lng').value);
    if (!isNaN(lat) && !isNaN(lng)) {
        setMarker(lat, lng);
    } else {
        alert("Please enter valid latitude and longitude.");
    }
}

function sendLocation(lat, lng) {
    if (window.pywebview && window.pywebview.api) {
        console.log("Sending coordinates to pywebview:", lat, lng);
        window.pywebview.api.send_coordinates(lat, lng);
    } else {
        console.warn("PyWebView API not ready. Skipping coordinate send.");
    }
}

map.on('click', function(e) {
    setMarker(e.latlng.lat, e.latlng.lng);
});

document.addEventListener("pywebviewready", function() {
    console.log("PyWebView is ready!");
    document.getElementById("toggleGeology").checked = true;
    toggleLayer(document.getElementById("toggleGeology"), wmsGeologyLayer);

    document.getElementById("toggleHydroMap").checked = true;
    toggleLayer(document.getElementById("toggleHydroMap"), wmsHydroEuropeLayer);
});
