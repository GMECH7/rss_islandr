import sys

import pytest

from dev_scripts import clean


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project folder with generated files, source files and a virtual environment."""
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "installer.deb").write_bytes(b"x" * 100)
    (tmp_path / "build").mkdir()
    (tmp_path / "rss_islandr.log").write_text("log")
    (tmp_path / "package" / "__pycache__").mkdir(parents=True)
    (tmp_path / "package" / "module.py").write_text("code")
    (tmp_path / ".venv" / "lib" / "__pycache__").mkdir(parents=True)
    (tmp_path / "README.md").write_text("readme")
    monkeypatch.setattr(clean, "ROOT_DIR", tmp_path)
    return tmp_path


def test_generated_files_are_found_but_not_the_venv_or_sources(project):
    """
    Steps:
    1. Create a project folder with `dist/`, `build/`, a log file, a source file, a `__pycache__` folder and a .venv
       with its own `__pycache__`.
    2. Search the generated files.

    Expected result:
    - Only `dist`, `build`, the log file and the `__pycache__` of the source folder are found.
    """
    found = {path.relative_to(project).as_posix() for path in clean.find_generated(project)}

    assert found == {"dist", "build", "rss_islandr.log", "package/__pycache__"}


def test_dry_run_removes_nothing(project):
    """
    Steps:
    1. Create the project folder.
    2. Run `clean --dry-run`.

    Expected result:
    - It returns 0 and every file and folder still exists.
    """
    assert clean.main(["--dry-run"]) == 0

    assert (project / "dist" / "installer.deb").exists()
    assert (project / "build").exists()


def test_clean_removes_generated_files_only(project):
    """
    Steps:
    1. Create the project folder.
    2. Run `clean`.

    Expected result:
    - `dist/`, `build/`, the log file and the source `__pycache__` are removed. The source file, the .venv (with its
      `__pycache__`) and the README remain.
    """
    assert clean.main([]) == 0

    assert not (project / "dist").exists()
    assert not (project / "build").exists()
    assert not (project / "rss_islandr.log").exists()
    assert not (project / "package" / "__pycache__").exists()
    assert (project / "package" / "module.py").exists()
    assert (project / ".venv" / "lib" / "__pycache__").exists()
    assert (project / "README.md").exists()


def test_clean_of_a_clean_project_does_nothing(tmp_path, monkeypatch):
    """
    Steps:
    1. Use an empty project folder.
    2. Run `clean`.

    Expected result:
    - It returns 0 without an error.
    """
    monkeypatch.setattr(clean, "ROOT_DIR", tmp_path)

    assert clean.main([]) == 0


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
