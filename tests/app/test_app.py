import sys

import pytest

from rss_islandr import app


@pytest.fixture(autouse=True)
def no_logger_setup(monkeypatch):
    """`run` sets up the logger of the app (log file, handlers): not wanted in the tests."""
    monkeypatch.setattr(app, "setup_logger", lambda *args, **kwargs: None)


def test_self_test_option_returns_the_result_of_the_self_test(monkeypatch, tmp_path):
    calls = []

    def fake_self_test(report_file):
        calls.append(report_file)
        return 3

    monkeypatch.setattr("rss_islandr.self_test.run_self_test", fake_self_test)
    report_file = str(tmp_path / "report.txt")

    assert app.run(["--self-test", "--self-test-report", report_file]) == 3
    assert calls == [report_file]


def test_map_process_option_starts_the_map_process(monkeypatch):
    calls = []
    monkeypatch.setattr("rss_islandr.ui.map_ui._run_map_process", lambda: calls.append("map"))

    assert app.run(["--map-process"]) == 0
    assert calls == ["map"]


def test_the_window_is_started_without_options(monkeypatch):
    calls = []
    monkeypatch.setattr(app, "start_ui", lambda: calls.append("ui"))

    assert app.run([]) == 0
    assert calls == ["ui"]


def test_unknown_option_is_rejected():
    with pytest.raises(SystemExit):
        app.parse_args(["--unknown"])


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
