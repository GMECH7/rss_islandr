import sys

import pytest

from rss_islandr import app


@pytest.fixture(autouse=True)
def no_logger_setup(monkeypatch):
    """`run` sets up the logger of the app (log file, handlers): not wanted in the tests."""
    monkeypatch.setattr(app, "setup_logger", lambda *args, **kwargs: None)


def test_self_test_option_returns_the_result_of_the_self_test(monkeypatch, tmp_path):
    """
    Steps:
    1. Replace `run_self_test` by a fake that returns 3.
    2. Run the app with `--self-test` and `--self-test-report <file>`.

    Expected result:
    - `run` returns 3 (the result of the self-test) and passes the report file to the self-test.
    """
    calls = []

    def fake_self_test(report_file):
        calls.append(report_file)
        return 3

    monkeypatch.setattr("rss_islandr.self_test.run_self_test", fake_self_test)
    report_file = str(tmp_path / "report.txt")

    assert app.run(["--self-test", "--self-test-report", report_file]) == 3
    assert calls == [report_file]


def test_map_process_option_starts_the_map_process(monkeypatch):
    """
    Steps:
    1. Replace the map process by a fake that records its call.
    2. Run the app with `--map-process`.

    Expected result:
    - The map process is started once and `run` returns 0.
    """
    calls = []
    monkeypatch.setattr("rss_islandr.ui.map_ui._run_map_process", lambda: calls.append("map"))

    assert app.run(["--map-process"]) == 0
    assert calls == ["map"]


def test_the_window_is_started_without_options(monkeypatch):
    """
    Steps:
    1. Replace `start_ui` by a fake that records its call.
    2. Run the app without options.

    Expected result:
    - The window is started once and `run` returns 0.
    """
    calls = []
    monkeypatch.setattr(app, "start_ui", lambda: calls.append("ui"))

    assert app.run([]) == 0
    assert calls == ["ui"]


def test_unknown_option_is_rejected():
    """
    Steps:
    1. Parse the command line `--unknown`.

    Expected result:
    - The parser exits (`SystemExit`) instead of starting the app.
    """
    with pytest.raises(SystemExit):
        app.parse_args(["--unknown"])


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
