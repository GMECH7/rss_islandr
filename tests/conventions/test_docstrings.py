import ast
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent.parent


def _test_functions():
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                yield path.relative_to(TESTS_DIR).as_posix(), node


def test_every_test_describes_its_steps_and_expected_result():
    """
    Steps:
    1. Go through all test functions in the tests folder.
    2. Read the docstring of each one.

    Expected result:
    - Every test has a docstring with a "Steps:" part (what is done) and an "Expected result:" part (what should
      happen). The failure message lists the tests that miss them.
    """
    undocumented = []
    for file, function in _test_functions():
        docstring = ast.get_docstring(function) or ""
        if "Steps:" not in docstring or "Expected result:" not in docstring:
            undocumented.append(f"{file}::{function.name}")

    assert undocumented == []


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
