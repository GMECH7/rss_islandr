import sys

import pytest

from dev_scripts import run


def test_islandr_command_exits_with_the_result_of_the_app(monkeypatch):
    monkeypatch.setattr(run, "run", lambda: 5)

    with pytest.raises(SystemExit) as exit_info:
        run.main()

    assert exit_info.value.code == 5


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
