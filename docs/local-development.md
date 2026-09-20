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
    - [10.1 Protecting `main`](#101-protecting-main)
    - [10.2 Jobs of the Installers workflow](#102-jobs-of-the-installers-workflow)
    - [10.3 Publishing a new version](#103-publishing-a-new-version)
    - [10.4 Checking a run](#104-checking-a-run)
    - [10.5 Reproducibility](#105-reproducibility)
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

```text
rss_islandr/                      Project root
├── .github/workflows/            The GitHub workflows
├── build_installer/              Everything that creates the installers
│   ├── docker/                   Ubuntu 24.04 build image and script
│   ├── installer/islandr.iss     Inno Setup script of the Windows installer
│   ├── pyi_rth_tcl_modules.py    PyInstaller runtime hook
│   └── ...                       The other Python modules of the rss-build command
├── dev_scripts/                  Scripts used during development, each one is a Poetry command
├── docs/                         This documentation
├── rss_islandr/                  The application
│   ├── assessment/               The risk calculation
│   ├── core/                     Shared code: data types, settings, logging, platform setup
│   ├── data/                     Weights and settings as JSON
│   ├── data_readers/             Reads the risk factors and their weights
│   ├── maps/                     The Leaflet map page
│   ├── reporting/                The PDF report
│   ├── templates/                The Excel template
│   ├── ui/                       Windows, tabs and buttons
│   ├── app.py                    Starts the application and handles the command line options
│   └── self_test.py              The installation check (--self-test)
├── tests/                        The tests, one folder per part of the code
├── islandr.spec                  PyInstaller specification
├── main.py                       Entry point of the application
├── poetry.lock, poetry.toml      Locked versions and Poetry settings
└── pyproject.toml                Dependencies, commands and version
```

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
| `poetry run clean` | Removes the generated files: `dist/`, `build/`, `.cov_files/`, caches, `rss_islandr.log` and `version_info.txt`. `--dry-run` only lists them. The built installers in `dist/` are removed as well, but `.venv/` is never removed |
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

> [!NOTE]
> The user interface tests create real windows and need a display. The Ubuntu CI job runs them under `xvfb-run` (virtual display, see `.github/workflows/ci.yml`).

When writing new tests, the developer should give in each one a docstring with two parts: **Steps** (what the test does) and **Expected result** (what should happen).

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

A test that lacks either part makes `pytest` fail, because `tests/conventions/test_docstrings.py` checks every test.

## 8. Managing dependencies

If the project needs a new package, use the following commands as a quick cheatsheet:

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

The version of the application is the `version` in `pyproject.toml`, in the form `X.Y.Z`. It is updated by hand and is used for the installers, the file properties of the Windows executable and the name of the release (`v<version>`).

## 10. GitHub workflows and releases

Two workflows are in `.github/workflows/`.

| Workflow | File | Runs on | Jobs |
|---|---|---|---|
| Tests | `ci.yml` | Pull requests to `main` (before the merge), merges into `main`, and the **Run workflow** button | `pytest` on Ubuntu 24.04 and on Windows 2022 |
| [Installers](#102-jobs-of-the-installers-workflow) | `release.yml` | Merges into `main` and the **Run workflow** button | Version and release check, Ubuntu package, Windows installer and publication of the release |

Both files contain a commented-out trigger for the branch `makge/publication`. Removing the `#` runs the workflow on pushes to that branch, which is useful to try changes to a workflow before it is on `main`.

### 10.1 Protecting `main`

A merge into `main` publishes a release, so `main` can only change through a pull request: the changes are made on a separate branch and merged after a review and passing tests. The branch is protected by the following rules:

1. A pull request is required before merging, with at least one approval.
2. The two jobs of the Tests workflow, `pytest (ubuntu-24.04)` and `pytest (windows-2022)`, **MUST PASS** before merging. The names of the required checks match the job names in `ci.yml`.
3. Force pushes to the branch and its deletion are blocked.
4. The rules apply to administrators as well, so nobody can push directly to `main`.

The rules are configured in the repository settings under *Settings → Rules → Rulesets*.

The merge of a pull request triggers the Installers workflow as described below (GitHub reports the merge as a push event to `main`). The publishing job creates a tag and a release with `gh release create` and does not push commits, so the rules do not block it.

### 10.2 Jobs of the Installers workflow

1. **Version and release check:** reads `version` from `pyproject.toml` and checks whether the release `v<version>` exists.
2. **Ubuntu package:** builds the `.deb` in the Ubuntu 24.04 container (`rss-build --deb --docker`) and tests it in clean Ubuntu 24.04 and 26.04 containers (`rss-build --test-deb`).
3. **Windows installer:** builds `islandr-setup.exe` and `islandr-portable.zip` (`rss-build --win`). It then installs the installer silently, runs the self-test of the installed application, uninstalls it and checks that nothing remains. The self-test is also run on the unzipped portable version.
4. **Publish the release:** runs only after a merge into `main` when the release does not exist yet. It creates the tag and the GitHub release `v<version>` with `islandr-setup.exe`, `islandr-portable.zip`, `rss-islandr_<version>_amd64.deb` and `SHA256SUMS.txt`, with automatically generated release notes.

### 10.3 Publishing a new version

1. Create a branch from `main`, for example `git switch -c dev_g1/new_feature`, and change `version` in `pyproject.toml`.
2. Push the branch and open a pull request to `main`. The tests run on the pull request.
3. Merge the pull request after the review. The Installers workflow runs and creates the release.
4. Check the run in the Actions tab of the repository and the new release on the [Releases page](https://github.com/GMECH7/rss_islandr/releases).

> [!IMPORTANT]
> A merge into `main` with a version that is already released builds and tests the installers but does not publish. A release that has been published is never replaced. To correct a release, delete the release and its tag on GitHub, or publish a new version.

### 10.4 Checking a run

- **Actions tab:** every run lists its jobs with the full log. The run page has a summary with the size and SHA-256 checksum of each file.
- **Artifacts:** the files of a run that did not publish a release are attached to the run page under *Artifacts* (`ubuntu-package`, `windows-installer`) for 14 days. GitHub delivers an artifact as a zip file, and downloading requires a GitHub login. The commands for the checksum check and the installation are in [Installers](installers.md#31-checking-the-download) and [Installers](installers.md#4-installing-and-uninstalling).
- **Releases page:** [github.com/GMECH7/rss_islandr/releases](https://github.com/GMECH7/rss_islandr/releases) holds the permanent files. GitHub allows each release file to be up to 2 GiB and states no limit for the total size of a release.

### 10.5 Reproducibility

The runner images are fixed (`ubuntu-24.04`, `windows-2022`) as well as Python 3.12, Poetry 2.4.1 (with `poetry.lock`) and Inno Setup 6.7.1. The Ubuntu package is built in the same Ubuntu 24.04 container image that is used locally.

If the release job fails with a permission error, check that the repository setting *Settings, Actions, General, Workflow permissions* allows the workflow to write.

## 11. Notes

- **Slow start on Ubuntu.** On some Ubuntu desktops the application took minutes to open because of the keyboard input system (ibus). For this reason the application does not use it, and this affects only the application itself, not the rest of the system. As a result, input methods such as those for Chinese or Japanese cannot be used to type in the application. To keep the input system, start the application with the environment variable `RSS_KEEP_INPUT_METHOD=1`.
- **Visual Studio Code.** The file `.vscode/settings.json` selects the virtual environment in `.venv`. On Windows, start Visual Studio Code from Windows PowerShell and not from an Anaconda prompt, otherwise the environment may not be activated.
- **Logging.** When the application runs from source it writes `rss_islandr.log` in the current folder. Logging is disabled in the installed application.
