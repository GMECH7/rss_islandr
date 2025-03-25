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

### Setting Up a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies for this project. A `requirements.txt` file is provided to simplify the setup process.

Follow these steps to set up the virtual environment:

1. **Navigate to the project directory**:
   ```bash
   cd <local-project-directory>
   ```
2. **Create a virtual environment**:

   ```bash
   python -m venv islandr_env
   ```

3. **Activate the Virtual Environment**:

   - If you are using **Visual Studio Code (VSC)**, the virtual environment should activate automatically due to the presence of the `.vscode/settings.json` file.
   - Otherwise, activate the environment manually:
     - On **Windows**:
       ```bash
       islandr_env\Scripts\activate
       ```
     - On **macOS/Linux**:
       ```bash
       source islandr_env/bin/activate
       ```

4a. **Install the required dependencies (using pip)**:

```bash
pip install -r requirements.txt
```

4b. **Install the required dependencies (using poetry)**:

```bash
poetry install
```

## References

- **New Zealand Ministry for the Environment**: [Contaminated Land Management Guidelines No. 3 – Risk Screening System](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/)
- **Source-Pathway-Receptor (SPR) Model**: A foundational framework for environmental risk assessment.
