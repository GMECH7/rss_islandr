import sys

import pytest

from rss_islandr.core.helpers import extract_dicts_from_string


def test_dictionaries_are_read_from_a_text():
    """
    Steps:
    1. Give a text with two dictionaries written one after the other.

    Expected result:
    - The result is a list with the two dictionaries.
    """
    assert extract_dicts_from_string("{'a': 1}{'b': 2}") == [{"a": 1}, {"b": 2}]


def test_list_text_and_separators_are_ignored():
    """
    Steps:
    1. Give the text of a list of dictionaries with commas, brackets and other text between them.

    Expected result:
    - Only the dictionaries are returned.
    """
    assert extract_dicts_from_string("[{'a': 1}, text {'b': 2}]") == [{"a": 1}, {"b": 2}]


def test_nested_dictionary_stays_inside_its_parent():
    """
    Steps:
    1. Give a dictionary that contains another dictionary.

    Expected result:
    - One dictionary is returned, with the inner one as a value.
    """
    assert extract_dicts_from_string("{'a': {'b': 1}, 'c': 2}") == [{"a": {"b": 1}, "c": 2}]


def test_text_without_dictionaries_gives_an_empty_list():
    """
    Steps:
    1. Give an empty text and a text without braces.

    Expected result:
    - Both results are empty lists.
    """
    assert extract_dicts_from_string("") == []
    assert extract_dicts_from_string("no dictionary here") == []


def test_dictionary_that_cannot_be_read_raises_an_error():
    """
    Steps:
    1. Give a text with balanced braces that is not a valid dictionary.

    Expected result:
    - An error is raised that starts with "Failed to parse" and shows the text.
    """
    with pytest.raises(Exception, match="Failed to parse: {'a': }"):
        extract_dicts_from_string("{'a': }")


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
