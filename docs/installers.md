# Installers

This document describes how the installers are built on a local machine, how they are installed and removed, and how the finished installers are downloaded from GitHub. The development setup is described in [Local development](local-development.md).

Contents

1. [Overview](#1-overview)
2. [Building the installers locally](#2-building-the-installers-locally)
3. [Installing and uninstalling a local build](#3-installing-and-uninstalling-a-local-build)
4. [Downloading a release from GitHub](#4-downloading-a-release-from-github)
5. [Checking an installation](#5-checking-an-installation)
6. [Troubleshooting](#6-troubleshooting)

## 1. Overview

The installers are created by the command `poetry run rss-build` (code in `build_installer/`). The version of the installers is `version` in `pyproject.toml`.

| System | File | Created by | Built on |
|---|---|---|---|
| Windows 10/11 | `islandr-setup.exe` (installer) | `rss-build --win` | Windows |
| Windows 10/11 | `islandr-portable.zip` (no installation) | `rss-build --win` | Windows |
| Ubuntu 24.04 or later | `rss-islandr_<version>_amd64.deb` | `rss-build --deb` | Linux |

All files are written to the folder `dist/`. The installers are built with PyInstaller (one-folder build described in `islandr.spec`). PyInstaller cannot build for another system, so each installer has to be built on its own system.

The same commands run in the GitHub workflow that creates the releases (see [Local development](local-development.md#10-github-workflows-and-releases)).

## 2. Building the installers locally

Prepare the development environment first (see [Local development](local-development.md)):

```bash
poetry install
```

### Ubuntu package

**Prerequisites:** Docker for the recommended build. The build image is Ubuntu 24.04, the oldest supported system. A program built on an older system also runs on newer ones, but not the other way round.

Build in a container (recommended, this is the same environment as in the workflow):

```bash
sudo apt install docker.io
sudo usermod -aG docker $USER      # then log out and in again
poetry run rss-build --deb --docker
```

Build with the local system instead (no Docker; the result then depends on the installed Ubuntu version and libraries):

```bash
poetry run rss-build --deb
```

Test the package in clean Ubuntu 24.04 and 26.04 containers (needs Docker):

```bash
poetry run rss-build --test-deb
```

The test installs the package with `apt`, runs the self-test of the installed application, checks that no system library is missing, starts the map process and checks that it keeps running, and removes the package again.

Result: `dist/rss-islandr_<version>_amd64.deb`. The package installs the application to `/opt/rss-islandr`, the command `rss-islandr` and an entry in the application menu. The size is about 155 MB, mostly the bundled Qt WebEngine.

### Windows installer and portable zip

**Prerequisites:** Windows 10/11 and [Inno Setup 6](https://jrsoftware.org/isinfo.php). The workflow uses version 6.7.1. Install it with an installer from the website or with Chocolatey:

```powershell
choco install innosetup --version=6.7.1 -y
```

The build finds `ISCC.exe` on the `PATH` or in `C:\Program Files (x86)\Inno Setup 6`.

```powershell
poetry run rss-build --win
```

Result: `dist\islandr-setup.exe` and `dist\islandr-portable.zip`. The script of the installer is `build_installer/installer/islandr.iss`.

### What the build does

1. Reads the version from `pyproject.toml` and writes `version_info.txt` (file properties of the Windows executable).
2. Runs PyInstaller with `islandr.spec`. The result is the folder `dist/islandr/`.
3. Runs the self-test of the built application (`islandr --self-test`). If it fails, the build fails.
4. Creates the package: the `.deb` (Debian package with menu entry, icon and the list of required system libraries), or the Windows installer and the portable zip.

To remove the results of a build, run `poetry run clean` (see [Local development](local-development.md#6-commands)).

## 3. Installing and uninstalling a local build

### Ubuntu

```bash
# Install (also replaces an installed version with the version of the file)
sudo apt install ./dist/rss-islandr_<version>_amd64.deb

# Install an older version than the installed one
sudo apt install --allow-downgrades ./dist/rss-islandr_<version>_amd64.deb

# Start (or use the application menu entry "RSS-ISLANDR")
rss-islandr

# Installed version
dpkg -l rss-islandr

# Uninstall
sudo apt remove rss-islandr
sudo apt purge rss-islandr     # also removes configuration files (the application has none)
```

### Windows

```powershell
# Install with the wizard, or silently
.\dist\islandr-setup.exe
.\dist\islandr-setup.exe /VERYSILENT /NORESTART

# Uninstall: Settings > Apps > RSS-ISLANDR, or silently
& "$env:LOCALAPPDATA\Programs\RSS-ISLANDR\unins000.exe" /VERYSILENT
```

The installer installs for the current user without administrator rights. The default folder is `%LOCALAPPDATA%\Programs\RSS-ISLANDR`. Installing another version over an installed one upgrades it.

**Portable version:** unzip `islandr-portable.zip` and run `islandr\islandr.exe`. To remove it, delete the folder.

## 4. Downloading a release from GitHub

This is the way for users. The installers are built by the GitHub workflow, published on the Releases page and do not need to be built locally. Each release `v<version>` contains:

| File | System |
|---|---|
| `islandr-setup.exe` | Windows 10/11 (installer) |
| `islandr-portable.zip` | Windows 10/11 (no installation) |
| `rss-islandr_<version>_amd64.deb` | Ubuntu 24.04 or later |
| `SHA256SUMS.txt` | Checksums of the files above |

The Releases page is `https://github.com/GMECH7/rss_islandr/releases`. Releases do not expire, and a specific version can be selected on that page.

The installers are not code-signed. Windows may show the message "Windows protected your PC": select *More info* and then *Run anyway*.

### Ubuntu 24.04 or later

```bash
# Download a specific version and the checksums (here 1.22.1)
VERSION=1.22.1
wget https://github.com/GMECH7/rss_islandr/releases/download/v$VERSION/rss-islandr_${VERSION}_amd64.deb
wget https://github.com/GMECH7/rss_islandr/releases/download/v$VERSION/SHA256SUMS.txt

# Check the download; the line for the .deb must end with OK
sha256sum -c SHA256SUMS.txt --ignore-missing

# Install
sudo apt install ./rss-islandr_${VERSION}_amd64.deb

# Start, check the version, uninstall
rss-islandr
dpkg -l rss-islandr
sudo apt remove rss-islandr
```

To install an older version than the installed one, add `--allow-downgrades` to the install command.

### Windows 10/11

Download `islandr-setup.exe` (or the zip) and `SHA256SUMS.txt` from the release page, then in PowerShell:

```powershell
# Check the download and compare the value with the line of the file in SHA256SUMS.txt
Get-FileHash .\islandr-setup.exe -Algorithm SHA256
certutil -hashfile islandr-setup.exe SHA256        # alternative

# Install (or double-click the file)
.\islandr-setup.exe

# Uninstall: Settings > Apps > RSS-ISLANDR, or
& "$env:LOCALAPPDATA\Programs\RSS-ISLANDR\unins000.exe" /VERYSILENT
```

### Files of a workflow run

A run of the workflow that does not publish a release (for example a manual run) keeps the files as *Artifacts* on the run page in the Actions tab for 14 days. GitHub delivers each artifact as a zip file, so unzip it first. The run page shows the SHA-256 checksum of every file. The commands above then apply to the unzipped files. Only published releases are permanent.

## 5. Checking an installation

The self-test checks the data files, the risk calculation, the Excel template, the web engine of the map viewer and that the main window can be built.

```bash
# Ubuntu (installed package)
rss-islandr --self-test
```

```powershell
# Windows (installed application; the application has no console, so the result is written to a file)
& "$env:LOCALAPPDATA\Programs\RSS-ISLANDR\islandr.exe" --self-test --self-test-report "$env:TEMP\self_test.txt"
Get-Content "$env:TEMP\self_test.txt"
```

Exit code 0 and the last line "Self-test passed" mean that everything is in order. When a check fails, its line begins with `FAIL` and shows the error.

The version of an installed application is shown in the **Version** menu of the navigation bar (next to Documents).

## 6. Troubleshooting

| Problem | Explanation |
|---|---|
| The Ubuntu window stays blank or takes minutes to appear | Caused by the input method (ibus). The application switches it off. Make sure the variable `RSS_KEEP_INPUT_METHOD` is not set |
| `apt` reports a missing dependency | The system is older than Ubuntu 24.04, or the package lists are outdated: run `sudo apt update` |
| The map window shows no map | The map needs an internet connection. The layers come from external services |
| "Save the map" does nothing on Ubuntu | The button is not available with the Qt WebEngine; use the screenshot tool of the operating system |
| Windows shows "Windows protected your PC" | The installer is not code-signed: select *More info* and *Run anyway* |
