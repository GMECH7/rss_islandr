document.addEventListener("DOMContentLoaded", function () {
    const map = window.map || L.map('map').setView([0, 0], 2); // fallback if `map` isn't globally set

    // Add a simple tile layer if none exists (just in case)
    if (!map.hasLayer) {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19
        }).addTo(map);
    }

    // Draw control
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        draw: {
            polyline: false,
            polygon: false,
            circle: false,
            circlemarker: false,
            marker: false,
            rectangle: {
                shapeOptions: {
                    color: '#ff0000'
                }
            }
        },
        edit: {
            featureGroup: drawnItems,
            edit: false,
            remove: true
        }
    });

    map.addControl(drawControl);

    let selectedBounds = null;

    map.on(L.Draw.Event.CREATED, function (event) {
        drawnItems.clearLayers();
        const layer = event.layer;
        drawnItems.addLayer(layer);
        selectedBounds = layer.getBounds();
    });

    document.getElementById("screenshotBtn").addEventListener("click", async () => {
        if (!selectedBounds) {
            alert("Draw a rectangle first to define the area to capture.");
            return;
        }

        // Zoom to selected bounds
        map.fitBounds(selectedBounds);

        // Wait a moment for tiles to load (not perfect, but works for most)
        await new Promise(resolve => setTimeout(resolve, 1000));

        const mapContainer = document.getElementById("map");

        html2canvas(mapContainer, {
            useCORS: true
        }).then(canvas => {
            // Create download link
            canvas.toBlob(function (blob) {
                const a = document.createElement("a");
                const url = URL.createObjectURL(blob);

                a.href = url;
                a.download = "map_capture.png";

                // Trigger native dialog
                a.click();

                // Cleanup
                URL.revokeObjectURL(url);
            }, "image/png");
        });
    });
});
