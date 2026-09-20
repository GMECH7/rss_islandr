# Installers

This document describes how the installers are built on a local machine, how the finished installers are downloaded from GitHub, and how they are installed and removed. The development setup is described in [Local development](local-development.md).

## Table of Contents

1. [Overview](#1-overview)
2. [Building the installers locally](#2-building-the-installers-locally)
    - [2.1 What every build does](#21-what-every-build-does)
    - [2.2 Ubuntu package](#22-ubuntu-package)
    - [2.3 Windows installer and portable zip](#23-windows-installer-and-portable-zip)
3. [Downloading a release from GitHub](#3-downloading-a-release-from-github)
    - [3.1 Checking the download](#31-checking-the-download)
4. [Installing and uninstalling](#4-installing-and-uninstalling)
    - [4.1 Ubuntu](#41-ubuntu)
    - [4.2 Windows](#42-windows)
        - [4.2.1 Installer](#421-installer)
        - [4.2.2 Portable version](#422-portable-version)
5. [Checking an installation](#5-checking-an-installation)
6. [Troubleshooting](#6-troubleshooting)

## 1. Overview

The installers are created by the command `poetry run rss-build` (code in `build_installer/`). The version of the installers is `version` in `pyproject.toml`.

| System | File | Created by | Built on |
|---|---|---|---|
| Windows 10/11 | `islandr-setup.exe` (installer) | `rss-build --win` | Windows |
| Windows 10/11 | `islandr-portable.zip` (no installation) | `rss-build --win` | Windows |
| Ubuntu 24.04 or later | `rss-islandr_<version>_amd64.deb` | `rss-build --deb` | Linux |

All files are written to the folder `dist/`. The installers are built with PyInstaller (one-folder build described in `islandr.spec`).

> [!NOTE]
> PyInstaller cannot build for another system, so each installer has to be built on its own system.

The same commands run in the GitHub workflow that creates the releases (see [Local development](local-development.md#10-github-workflows-and-releases)).

## 2. Building the installers locally

Prepare the development environment first (see [Local development](local-development.md)):

```bash
poetry install
```

### 2.1 What every build does

1. Reads the version from `pyproject.toml` and writes `version_info.txt` (file properties of the Windows executable).
2. Runs PyInstaller with `islandr.spec`. The result is the folder `dist/islandr/`.
3. Runs the self-test of the built application (`islandr --self-test`). If it fails, the build fails.
4. Creates the package: the `.deb` (Debian package with menu entry, icon and the list of required system libraries), or the Windows installer and the portable zip.

At the end, the build prints a table with the created files and their sizes. The platform-specific parts follow.

### 2.2 Ubuntu package

**Prerequisites:** Docker for the recommended build. The build image is Ubuntu 24.04, the oldest supported system. A program built on an older system also runs on newer ones, but not the other way round.

Build in a container (recommended, this is the same environment as in the workflow):

```bash
sudo apt install docker.io
sudo usermod -aG docker $USER      # then log out and in again
poetry run rss-build --deb --docker
```

Build with the local system instead. This does not use Docker, so the result depends on the installed Ubuntu version and libraries:

```bash
poetry run rss-build --deb
```

Test the package in clean Ubuntu 24.04 and 26.04 containers (needs Docker):

```bash
poetry run rss-build --test-deb
```

In each container the test does the following:

1. Installs the package with `apt`.
2. Runs the self-test of the installed application.
3. Checks that no system library is missing.
4. Starts the map process and checks that it is still running after 10 seconds.
5. Removes the package and checks that the installation folder is gone.

The result is `dist/rss-islandr_<version>_amd64.deb`. The package provides:

- The application in `/opt/rss-islandr`.
- The command `rss-islandr`.
- An entry in the application menu.

The size is about 155 MB, mostly the bundled Qt WebEngine.

### 2.3 Windows installer and portable zip

**Prerequisites:** Windows 10/11 and [Inno Setup 6](https://jrsoftware.org/isinfo.php). The workflow uses version 6.7.1. Install it with an installer from the website or with Chocolatey, which is how the GitHub workflow installs it:

```powershell
choco install innosetup --version=6.7.1 -y
```

The build finds `ISCC.exe` on the `PATH` or in `C:\Program Files (x86)\Inno Setup 6`.

```powershell
poetry run rss-build --win
```

The result is two files in the folder `dist\`:

- `islandr-setup.exe`, the installer.
- `islandr-portable.zip`, the version that needs no installation.

The script of the installer is `build_installer/installer/islandr.iss`.

To remove the results of a build, run `poetry run clean` (see [Local development](local-development.md#6-commands)).

## 3. Downloading a release from GitHub

End users can use directly the installers built by the GitHub workflow, published on the [Releases page](https://github.com/GMECH7/rss_islandr/releases) and do not need to be built locally. Each release `v<version>` contains:

| File | System |
|---|---|
| `islandr-setup.exe` | Windows 10/11 (installer) |
| `islandr-portable.zip` | Windows 10/11 (no installation) |
| `rss-islandr_<version>_amd64.deb` | Ubuntu 24.04 or later |
| `SHA256SUMS.txt` | Checksums of the files above |

The [Releases page](https://github.com/GMECH7/rss_islandr/releases) lists all versions. Releases do not expire, and a specific version can be selected on that page.

> [!NOTE]
> The installers are not code-signed. Windows may show the message "Windows protected your PC": select *More info* and then *Run anyway*.

After the download and the checksum check, install the file as described in section 4.

### 3.1 Checking the download

Download the files from the [Releases page](https://github.com/GMECH7/rss_islandr/releases) by selecting them, and download `SHA256SUMS.txt` as well. 

To check that a file is intact, compare its SHA-256 checksum with the line of the file in `SHA256SUMS.txt`.

**Ubuntu**: Use the terminal inside the folder with the downloaded files:

```bash
# The line for the .deb must end with OK
sha256sum -c SHA256SUMS.txt --ignore-missing
```

**Windows**: Use PowerShell in the folder with the downloaded files:

```powershell
# Compare the value with the line of the file in SHA256SUMS.txt
Get-FileHash .\islandr-setup.exe -Algorithm SHA256
certutil -hashfile islandr-setup.exe SHA256        # alternative
```

## 4. Installing and uninstalling

The commands apply to a file downloaded from a release (section 3) and to a local build in the folder `dist/` (section 2). Run them in the folder that contains the file.

### 4.1 Ubuntu

Install. This also replaces an installed version with the version of the file:

```bash
sudo apt install ./rss-islandr_<version>_amd64.deb
```

Install an older version than the installed one:

```bash
sudo apt install --allow-downgrades ./rss-islandr_<version>_amd64.deb
```

Start the application (or use the application menu entry "RSS-ISLANDR"):

```bash
rss-islandr
```

Show the installed version:

```bash
dpkg -l rss-islandr
```

Uninstall:

```bash
sudo apt remove rss-islandr
```

### 4.2 Windows

#### 4.2.1 Installer

Install with the wizard (or double-click the file):

```powershell
.\islandr-setup.exe
```

Uninstall with Settings > Apps > RSS-ISLANDR.

The installer installs for the current user without administrator rights. The default folder is `%LOCALAPPDATA%\Programs\RSS-ISLANDR`. Installing another version over an installed one upgrades it.

#### 4.2.2 Portable version

Unzip `islandr-portable.zip` and run `islandr\islandr.exe`. To remove it, delete the folder.

## 5. Checking an installation

The self-test checks the data files, the risk calculation, the Excel template, the web engine of the map viewer and that the main window can be built.

```bash
# Ubuntu (installed package)
rss-islandr --self-test
```

```powershell
# Windows (installed application). The application has no console, so the result is written to a file
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
| "Save the map" does nothing on Ubuntu | The button is not available with the Qt WebEngine. Use the screenshot tool of the operating system |
| Windows shows "Windows protected your PC" | The installer is not code-signed: select *More info* and *Run anyway* |
