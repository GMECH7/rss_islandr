# Risk Screening System (RSS)

## Overview

This repository contains a Python-based implementation of the **Risk Screening System (RSS)**, originally developed by the [New Zealand Ministry for the Environment](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/).

The Risk Screening System (RSS) evaluates environmental risks using a risk equation composed of three key components:

1. **Hazard (Source)**: The origin of the potential contamination.
2. **Exposure Pathway**: The route through which the hazard reaches the receptor.
3. **Receptor**: The entity (e.g., human, ecosystem) that may be affected by the hazard.

This framework is commonly referred to as the **Source-Pathway-Receptor (SPR)** model.

---

## Codebase

### Downloading the Repository

To download the repository locally, use the following command:

```bash
git clone https://github.com/GMECH7/rss_islandr.git
```

### Installing dependencies and execution

#### 1. Setup virtual environment

Follow these steps to set up the virtual environment:

a. **Navigate to the project directory**:

```bash
cd <local-project-directory>
```

b. **Create a virtual environment**:

```bash
python -m venv islandr_venv
```

c. **Activate the Virtual Environment**:

- If you are using **Visual Studio Code (VSC)**, the virtual environment should activate automatically due to the presence of the `.vscode/settings.json` file.
- Otherwise, activate the environment manually:
  - On **Windows**:
    ```bash
    islandr_venv\Scripts\activate
    ```
  - On **macOS/Linux**:
    ```bash
    source islandr_venv/bin/activate
    ```

d. Choose over **2a** and **2b** to install locally all dependencies (**2b** recommended)

#### 2a. Install dependencies using pip (depends on `requirements.txt`)

- **Install the required dependencies**:

```bash
pip install -r requirements.txt
```

- **Update requirements.txt**:

```bash
pip freeze > requirements.txt
```

#### 2b. Install dependencies using poetry (depends on `poetry.lock`)

- **Install the required dependencies**:

```bash
poetry install
```

- **Update poetry.lock**:

```bash
poetry lock
```

#### Advantages & disadvantages of poetry over pip

### ✅ Advantages

- **Reproducible environments**:  
  `poetry.lock` guarantees exact dependency versions used in development
- **Dependency resolution**: Handles complex dependency graphs better than pip
- **All-in-one tool**: Manages virtualenvs, packaging, and publishing

### ⚠️ Disadvantages

- **Environment conflicts**: Potential confusion with Anaconda/manual virtualenvs
- **Learning curve**: Different workflow from standard pip/virtualenv

#### Useful notes

1. **Regarding Windows & VSC integration:**

   - Use `Windows powershell` (not `Anaconda powershell`) to open VSC.
   - If VSC is opened through `Anaconda powershell` there may be difficulties in activating the virtual environment.

2. **Checking local environments:**

   - Make sure that poetry "sees" the rss_islandr environment. For that make use of the `poetry env info` command.

3. **More on poetry & pip**:

   - The package itself will not be shown after executing `poetry show` since this command visualizes only the dependencies of the `pyproject.toml` file. Instead the `poetry version` command should return the installed version of the package. Also the validation of the installation can be done by typing `pip list` command, which should return all packages installed in the virtual environment.

   - The installation of package through `poetry`is being made in editable mode.

   - If a new package is needed then the following commands are to be used:
     ```bash
     poetry add <package name> --dry-run # checks installation for conflicts
     poetry add <package name> # Adds the new dependency to .toml while installing in venv
     poetry remove <package name>
     or
     pip uninstall <package name>
     poetry show --tree # shows dependencies relationships
     ```

## References

- **New Zealand Ministry for the Environment**: [Contaminated Land Management Guidelines No. 3 – Risk Screening System](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/)
- **Source-Pathway-Receptor (SPR) Model**: A foundational framework for environmental risk assessment.

# 🗺️ Maps Viewer - Geology, Mines & Hydrogeology

The map viewer option of this app is built using [Leaflet.js](https://leafletjs.com/) and displays various geospatial layers using WMS (Web Map Service).

---

## 🌐 Map Services Used

### 1. **Surface Geology**

- **Service URL:** `https://geoserver.geo-zs.si/egdi-surface-geology/gsmlp/wms`
- **Layer Name:** `gsmlp:GeologicUnitView_Lithology`

### 2. **Mines**

- **Service URL:** `https://data.geus.dk/egdi/wms/`
- **Layer Name:** `egdi_mines`

### 3. **Hydrogeological Map**

- **Service URL:** `https://services.bgr.de/wms/grundwasser/ihme1500/`
- **Layer Names:** `0,1,2`

### 4. Links

https://services.bgr.de/uebersicht/kurzlinks

## ➕ How to Add New Map Layers

To add additional WMS layers:

1. Open the `script.js` file.
2. Add a new WMS layer using the following format:

```js
var newLayer = L.tileLayer.wms("YOUR_WMS_SERVICE_URL", {
  layers: "YOUR_LAYER_NAME",
  format: "image/png",
  transparent: true,
  version: "1.3.0",
});
```

3. Add a checkbox in `index.html` to allow toggling:

```html
<div>
  <input
    type="checkbox"
    id="toggleNewLayer"
    onclick="toggleLayer(this, newLayer)"
  />
  <label for="toggleNewLayer">Your Layer Name</label>
</div>
```

4. If you want a legend, add an image like this:

```html
<img
  id="newLayerLegend"
  class="legend zoomable"
  src="your_legend_image.svg"
  alt="New Layer Legend"
/>
```

5. Optionally, modify the `toggleLayer()` function in `script.js` to show/hide the legend for your new layer.

## 🔍 How to Find Available Map Layers (WMS)

Follow these steps to discover what layers are available in any WMS service:

### 1. 🧭 Get the GetCapabilities URL

Every WMS service provides a `GetCapabilities` endpoint that returns an XML file describing all available layers.

**Format:**
https://your-wms-server-url?service=WMS&request=GetCapabilities

**Examples:**

- [Geology WMS](https://geoserver.geo-zs.si/egdi-surface-geology/gsmlp/wms?service=WMS&request=GetCapabilities)
- [Mines WMS](https://data.geus.dk/egdi/wms/?service=WMS&request=GetCapabilities)
- [Hydrogeology WMS](https://services.bgr.de/wms/grundwasser/ihme1500/?service=WMS&request=GetCapabilities)

### 2. 🔎 Open the URL in Your Browser

Opening the URL shows an **XML document** with many `<Layer>` entries. Look for:

```xml
<Layer>
  <Name>your_layer_name</Name>
  <Title>Human-readable title</Title>
</Layer>
```

```html
- Use the <Name> value in your WMS layer config
- <Title> helps identify what the layer represents
```
