import sys

import pytest

from rss_islandr import self_test


def test_required_files_exist():
    """
    Steps:
    1. Call `check_files`, which checks the data, template, map and static files of the app.

    Expected result:
    - No error is raised: all required files are present.
    """
    self_test.check_files()


def test_missing_file_is_reported(monkeypatch, tmp_path):
    """
    Steps:
    1. Add a file that does not exist to the list of required files.
    2. Call `check_files`.

    Expected result:
    - `FileNotFoundError` is raised and its message names the missing file.
    """
    monkeypatch.setitem(self_test.REQUIRED_FILES, "test file", tmp_path / "missing.txt")

    with pytest.raises(FileNotFoundError, match="test file"):
        self_test.check_files()


def test_self_test_passes_and_writes_report(monkeypatch, tmp_path, capsys):
    """
    Steps:
    1. Reduce the self-test to two checks that pass (files and risk calculation).
    2. Run the self-test with a report file.

    Expected result:
    - The exit code is 0, the report file contains 'Self-test passed' and the console shows 'OK    files'.
    """
    checks = [("files", self_test.check_files), ("risk", self_test.check_risk_calculation)]
    monkeypatch.setattr(self_test, "CHECKS", checks)
    report_file = tmp_path / "report.txt"

    assert self_test.run_self_test(str(report_file)) == 0
    assert "Self-test passed" in report_file.read_text()
    assert "OK    files" in capsys.readouterr().out


def test_self_test_fails_when_a_check_fails(monkeypatch, tmp_path):
    """
    Steps:
    1. Use two checks: one that raises an error and one that passes.
    2. Run the self-test with a report file.

    Expected result:
    - The exit code is 1. The report contains the failed check with its error, the check that passes still ran (OK)
      and the last line is 'Self-test FAILED'.
    """
    def broken_check():
        raise RuntimeError("boom")

    monkeypatch.setattr(self_test, "CHECKS", [("broken", broken_check), ("risk", self_test.check_risk_calculation)])
    report_file = tmp_path / "report.txt"

    assert self_test.run_self_test(str(report_file)) == 1
    report = report_file.read_text()
    assert "FAIL  broken: RuntimeError: boom" in report
    assert "OK    risk" in report  # The remaining checks still run
    assert "Self-test FAILED" in report


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
