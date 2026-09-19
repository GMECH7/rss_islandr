import sys

import pytest

from build_installer import cli, debian, version, windows


def test_version_is_read_from_pyproject():
    """
    Steps:
    1. Read the app version with `read_version`.

    Expected result:
    - It is the `version` of pyproject.toml.
    """
    assert version.read_version() == version.read_pyproject()["version"]


def test_invalid_version_is_rejected(monkeypatch):
    """
    Steps:
    1. Make pyproject.toml report the version '2.0' (not X.Y.Z).
    2. Read the app version.

    Expected result:
    - `ValueError` is raised, saying that the version must have the form X.Y.Z.
    """
    monkeypatch.setattr(version, "read_pyproject", lambda: {"version": "2.0"})

    with pytest.raises(ValueError, match="X.Y.Z"):
        version.read_version()


def test_version_info_has_four_part_version(monkeypatch, tmp_path):
    """
    Steps:
    1. Write the Windows version file for the version '2.10.3' into a temporary folder.
    2. Read the file.

    Expected result:
    - It contains the four-part version `(2, 10, 3, 0)` and the product version '2.10.3'.
    """
    monkeypatch.setattr(version, "ROOT_DIR", tmp_path)

    content = version.write_version_info("2.10.3").read_text(encoding="utf-8")

    assert "filevers=(2, 10, 3, 0)" in content
    assert "StringStruct('ProductVersion', '2.10.3')" in content


def test_cli_requires_exactly_one_target():
    """
    Steps:
    1. Parse the command line of `rss-build` without options.
    2. Parse it with both `--win` and `--deb`.

    Expected result:
    - Both times the parser exits (`SystemExit`): exactly one target must be given.
    """
    with pytest.raises(SystemExit):
        cli.parse_args([])
    with pytest.raises(SystemExit):
        cli.parse_args(["--win", "--deb"])


def test_docker_flag_is_only_for_deb():
    """
    Steps:
    1. Parse `--deb --docker`.
    2. Parse `--win --docker`.

    Expected result:
    - The first is accepted and has the docker flag set. The second exits (`SystemExit`).
    """
    assert cli.parse_args(["--deb", "--docker"]).docker
    with pytest.raises(SystemExit):
        cli.parse_args(["--win", "--docker"])


def test_inno_command_passes_version_and_folders():
    """
    Steps:
    1. Create the Inno Setup command for the version 2.0.0.

    Expected result:
    - It starts with the compiler, passes the version and the source folder as definitions, ends with the script
      `islandr.iss` and that script exists.
    """
    command = windows.inno_command("ISCC.exe", "2.0.0")

    assert command[0] == "ISCC.exe"
    assert "/DAppVersion=2.0.0" in command
    assert any(argument.startswith("/DSourceDir=") for argument in command)
    assert command[-1].endswith("islandr.iss")
    assert windows.INNO_SCRIPT.exists()


def test_inno_script_uses_a_stable_app_id_and_no_admin_rights():
    """
    Steps:
    1. Read the Inno Setup script.

    Expected result:
    - It has the fixed AppId (needed for upgrades and the uninstaller) and `PrivilegesRequired=lowest` (installation
      without administrator rights).
    """
    script = windows.INNO_SCRIPT.read_text(encoding="utf-8")

    assert "AppId={{8F4B2C6E-3D1A-4E7B-9A52-6C0D7E1F3B84}" in script
    assert "PrivilegesRequired=lowest" in script


@pytest.mark.skipif(sys.platform == "win32", reason="the package is built on Linux")
def test_deb_package_tree(monkeypatch, tmp_path):
    """
    Steps:
    1. Create a fake application folder.
    2. Create the file tree of the Debian package for the version 2.0.0.

    Expected result:
    - The control file has the package name, the version and the system libraries. The app is in `/opt/rss-islandr`,
      `/usr/bin/rss-islandr` links to it, and the menu entry, the icon and the copyright file exist. (Skipped on
      Windows.)
    """
    app_dir = tmp_path / "app"
    (app_dir / "_internal").mkdir(parents=True)
    (app_dir / "islandr").write_text("#!/bin/sh\n")
    monkeypatch.setattr(debian, "APP_DIR", app_dir)
    stage_dir = tmp_path / "stage"
    stage_dir.mkdir()

    debian._stage_package(stage_dir, "2.0.0")

    control = (stage_dir / "DEBIAN" / "control").read_text(encoding="utf-8")
    assert "Package: rss-islandr" in control
    assert "Version: 2.0.0" in control
    assert "libnss3" in control
    assert (stage_dir / "opt" / "rss-islandr" / "islandr").exists()
    assert (stage_dir / "usr" / "bin" / "rss-islandr").readlink().as_posix() == "/opt/rss-islandr/islandr"
    assert "Exec=rss-islandr" in (stage_dir / "usr/share/applications/rss-islandr.desktop").read_text()
    assert (stage_dir / "usr/share/icons/hicolor/256x256/apps/rss-islandr.png").exists()
    assert (stage_dir / "usr/share/doc/rss-islandr/copyright").exists()


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
