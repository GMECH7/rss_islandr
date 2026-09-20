# Local development

This document describes how to set up the development environment, the commands that are available, the tests, and the GitHub workflows including how a release is created. The procedure on building the Windows and Linux installers, as well as the installation steps for end users is described in [Installers](installers.md).

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting the code](#2-getting-the-code)
3. [Installing Poetry](#3-installing-poetry)
4. [Installing the dependencies](#4-installing-the-dependencies)
5. [Project layout](#5-project-layout)
6. [Commands](#6-commands)
7. [Tests](#7-tests)
8. [Managing dependencies](#8-managing-dependencies)
9. [Version](#9-version)
10. [GitHub workflows and releases](#10-github-workflows-and-releases)
11. [Notes](#11-notes)

## 1. Prerequisites

| Requirement | Notes |
|---|---|
| Git | To clone the repository |
| Python 3.12, 3.13 or 3.14 | The project declares `>=3.12,<3.15`. Python 3.12 is the version used in the workflows |
| Poetry 2.4.1 | Dependency and environment management (section 3) |
| Windows 10/11 or Ubuntu 24.04 or later | The supported systems. macOS is untested |
| Ubuntu only: Tk (`python3-tk`) | A system package that Poetry cannot install (see below) |
| Ubuntu only, for building the installer: Docker | Builds and tests the Ubuntu package (`rss-build --deb`, see [Installers](installers.md)) |
| Windows only, for building the installer: Inno Setup 6 | Compiles the Windows installer (`rss-build --win`, see [Installers](installers.md)) |

On Ubuntu, Tk (used by the main window) is a separate system package and cannot be installed by Poetry, because `tkinter` links against the system Tcl/Tk libraries. Install it with:

```bash
sudo apt install python3-tk
```

If the map viewer does not start on a minimal system, install the missing system libraries. The libraries required by the Qt WebEngine are listed under `DEPENDS` in `build_installer/debian.py`.

On Windows, Tk is included in the python.org installer, and the map viewer uses the Microsoft Edge WebView2 runtime, which is part of Windows 10/11.

## 2. Getting the code

The repository is public and can be cloned via the following command:

```bash
git clone https://github.com/GMECH7/rss_islandr.git
```

## 3. Installing Poetry

Poetry creates the virtual environment and installs the dependencies from `poetry.lock`, which guarantees the same versions on every machine. 

Install it by following the official instructions: [python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation). The workflows use Poetry 2.4.1, so use that version or a later 2.x release.

Open a new terminal and check the installation:

```bash
poetry --version
```

## 4. Installing the dependencies

```bash
poetry install
```

The dependencies are declared in `pyproject.toml` in three groups: the application itself, the development tools (tests, code checks and the development scripts) and the tools that build the installers. All groups are always installed. The project installs itself in editable mode, so changes in the source code apply immediately.

The virtual environment is created in the folder `.venv`, inside the project (setting in `poetry.toml`). Useful checks:

```bash
poetry env info      # which environment Poetry uses
poetry show          # installed dependencies
poetry version       # version of the application
```

## 5. Project layout

| Folder / file | Contents |
|---|---|
| `rss_islandr/` | The application. `app.py` starts the application and handles the command line options; `ui/`, `core/`, `assessment/`, `reporting/`, `data_readers/`; `data/` (weights and settings as JSON); `maps/` (Leaflet map page); `templates/` (Excel template); `self_test.py` |
| `dev_scripts/` | Scripts used during development. Each one is a Poetry command (section 6) |
| `build_installer/` | Everything that creates the installers: the `rss-build` code, `docker/` (Ubuntu 24.04 build image and script), `installer/islandr.iss` (Inno Setup script of the Windows installer) and the PyInstaller hook |
| `tests/` | The tests, in one folder per part of the code |
| `docs/` | This documentation |
| `.github/workflows/` | The GitHub workflows (section 10) |
| `main.py`, `islandr.spec` | Entry point of the application and the PyInstaller specification |
| `pyproject.toml`, `poetry.lock`, `poetry.toml` | Dependencies, commands, version and Poetry settings |

## 6. Commands

Run all commands from the project folder.

| Command | What it does |
|---|---|
| `poetry run islandr` | Starts the application from the source code (the same as `python main.py`) |
| `poetry run islandr --self-test` | Checks the installation and exits: data files, risk calculation, Excel template, web engine and main window. Exit code 0 means success. `--self-test-report FILE` also writes the result to a file |
| `poetry run pytest` | Runs the tests. Coverage reports are written to `.cov_files/` |
| `poetry run ruff check .` | Checks the code with Ruff (lint) |
| `poetry run ruff check --fix .` | Checks the code and corrects the problems that can be corrected automatically |
| `poetry run ruff format .` | Formats the code. `poetry run ruff format --check .` only lists the files that would change |
| `poetry run clean` | Removes the generated files: `dist/`, `build/`, `.cov_files/`, caches, `rss_islandr.log` and `version_info.txt`. `--dry-run` only lists them. The built installers in `dist/` are removed as well; `.venv/` is never removed |
| `poetry run rss-build --win` | Windows: builds the installer and the portable zip |
| `poetry run rss-build --deb [--docker]` | Ubuntu: builds the package (`--docker` builds it in an Ubuntu 24.04 container) |
| `poetry run rss-build --test-deb` | Ubuntu: installs the package in clean containers and tests it |

The `rss-build` commands are described in [Installers](installers.md).

## 7. Tests

The tests are in the folder `tests/`, one subfolder for each part of the code: `app/`, `assessment/`, `build_installer/`, `conventions/`, `core/`, `data_readers/`, `dev_scripts/` and `ui/`.

```bash
poetry run pytest                              # all tests
poetry run pytest tests/ui                     # one folder
poetry run pytest tests/core -k input_method   # tests that match a name
```

The user interface tests create real windows and need a display. On Linux without a display (for example on a server), run:

```bash
sudo apt install xvfb
xvfb-run -a poetry run pytest
```

**Convention.** Every test has a docstring with two parts: **Steps** (what the test does) and **Expected result** (what should happen).

```python
def test_dry_run_removes_nothing(project):
    """
    Steps:
    1. Create the project folder.
    2. Run `clean --dry-run`.

    Expected result:
    - It returns 0 and every file and folder still exists.
    """
```

The test `tests/conventions/test_docstrings.py` fails and lists the tests that lack one of the parts.

## 8. Managing dependencies

```bash
poetry add <package> --dry-run         # check for conflicts without installing
poetry add <package>                   # add to pyproject.toml and install
poetry add --group dev <package>       # add to a group
poetry remove <package>
poetry show --tree                     # dependency tree
poetry lock                            # update poetry.lock after a change in pyproject.toml
```

Commit `pyproject.toml` and `poetry.lock` together.

## 9. Version

The application has one version: `version` in `pyproject.toml`, in the form `X.Y.Z`. It is updated by hand. The same version is used for the installers, the file properties of the Windows executable and the name of the release (`v<version>`).

## 10. GitHub workflows and releases

Two workflows are in `.github/workflows/`.

| Workflow | File | Runs on | Jobs |
|---|---|---|---|
| Tests | `ci.yml` | Pull requests to `main` (before the merge), pushes to `main`, and the **Run workflow** button | `pytest` on Ubuntu 24.04 and on Windows 2022 |
| Installers | `release.yml` | Pushes to `main` and the **Run workflow** button | Version and release check; Ubuntu package; Windows installer; publication of the release |

Both files contain a commented-out trigger for the branch `makge/publication`. Removing the `#` runs the workflow on pushes to that branch, which is useful to try changes to a workflow before it is on `main`.

### Jobs of the Installers workflow

1. **Version and release check:** reads `version` from `pyproject.toml` and checks whether the release `v<version>` exists.
2. **Ubuntu package:** builds the `.deb` in the Ubuntu 24.04 container (`rss-build --deb --docker`) and tests it in clean Ubuntu 24.04 and 26.04 containers (`rss-build --test-deb`).
3. **Windows installer:** builds `islandr-setup.exe` and `islandr-portable.zip` (`rss-build --win`). It then installs the installer silently, runs the self-test of the installed application, uninstalls it and checks that nothing remains. The self-test is also run on the unzipped portable version.
4. **Publish the release:** runs only on a push to `main` when the release does not exist yet. It creates the tag and the GitHub release `v<version>` with `islandr-setup.exe`, `islandr-portable.zip`, `rss-islandr_<version>_amd64.deb` and `SHA256SUMS.txt`, with automatically generated release notes.

### Publishing a new version

1. Change `version` in `pyproject.toml`.
2. Open a pull request to `main`. The tests run on the pull request.
3. Merge the pull request. The Installers workflow runs and creates the release.
4. Check the run in the Actions tab of the repository and the new release on the Releases page.

A push to `main` with a version that is already released builds and tests the installers but does not publish. A release that has been published is never replaced. To correct a release, delete the release and its tag on GitHub, or publish a new version.

### Checking a run

- **Actions tab:** every run lists its jobs with the full log. The run page has a summary with the size and SHA-256 checksum of each file.
- **Artifacts:** the files of a run that did not publish a release are attached to the run page under *Artifacts* (`ubuntu-package`, `windows-installer`) for 14 days. GitHub delivers an artifact as a zip file, and downloading requires a GitHub login.
- **Releases page:** `https://github.com/GMECH7/rss_islandr/releases` holds the permanent files. GitHub allows each release file to be up to 2 GiB and states no limit for the total size of a release.

### Reproducibility

The runner images are fixed (`ubuntu-24.04`, `windows-2022`) as well as Python 3.12, Poetry 2.4.1 (with `poetry.lock`) and Inno Setup 6.7.1. The Ubuntu package is built in the same Ubuntu 24.04 container image that is used locally.

If the release job fails with a permission error, check that the repository setting *Settings, Actions, General, Workflow permissions* allows the workflow to write.

## 11. Notes

- **Input method on Linux.** The application switches off the X11 input method (ibus) for its own process, because with ibus the main window needs minutes to be built. Set the environment variable `RSS_KEEP_INPUT_METHOD=1` to keep it.
- **Visual Studio Code.** The file `.vscode/settings.json` selects the virtual environment in `.venv`. On Windows, start Visual Studio Code from Windows PowerShell and not from an Anaconda prompt, otherwise the environment may not be activated.
- **Message windows.** All message windows of the main application (information, error, question) are shown through `rss_islandr/ui/dialogs.py`, which uses the themed dialogs of ttkbootstrap and follows the dark/light theme. The map page has its own dialogs in `rss_islandr/maps/js/dialogs.js` (`AppDialog.alert`, `AppDialog.confirm`, `AppDialog.prompt`) with the same colours, instead of the dialogs of the browser engine. Use these and not `tkinter.messagebox` or `alert()`/`prompt()`, so all windows look the same. In tests, replace the functions of `rss_islandr.ui.dialogs` to avoid real windows.
- **Logging.** When the application runs from source it writes `rss_islandr.log` in the current folder. Logging is disabled in the installed application.
