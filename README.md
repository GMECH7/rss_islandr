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

#### Using pip

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

5. **Update the requirements**:
   ```bash
   pip freeze > requirements.txt
   ```

#### Using poetry

The option of installing dependencies using poetry also exist, but there are some advantages and disadvantages.

### ✅ Advantages
- **Reproducible environments**:  
  `poetry.lock` guarantees exact dependency versions used in development
- **Dependency resolution**: Handles complex dependency graphs better than pip
- **All-in-one tool**: Manages virtualenvs, packaging, and publishing

### ⚠️ Disadvantages
- **Environment conflicts**: Potential confusion with Anaconda/manual virtualenvs
- **Learning curve**: Different workflow from standard pip/virtualenv


1. **Steps to follow (Windows-VSC):**
   - Use `Windows powershell` (not `Anaconda powershell`) to open VSC.

2. **Follow steps 1-3 of the pip installation instructions**

3. **Check local environments**
   - Make sure that poetry "sees" the rss_islandr environment. For that make use of the `poetry env info`

4. **Install the required dependencies**:
   - If the local virtual environment is being used then use `poetry install` to install dependencies based on the `poetry.lock` file.

5. **Update the requirements**:
   - The installation is being made in editable mode. Also if packages have been added or removed form the installation the user has to use `poetry lock update` to update the lock file.

## References

- **New Zealand Ministry for the Environment**: [Contaminated Land Management Guidelines No. 3 – Risk Screening System](https://environment.govt.nz/publications/contaminated-land-management-guidelines-no-3-risk-screening-system/)
- **Source-Pathway-Receptor (SPR) Model**: A foundational framework for environmental risk assessment.
