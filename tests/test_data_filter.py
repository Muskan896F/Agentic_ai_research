# tests/test_data_filter.py
"""
Unit tests for DataFilter agent.
We mock filtering behavior so tests don’t rely on external data.
"""

import pytest
from agents.data_filter import DataFilter


def test_filter_removes_empty_entries():
    """Ensure empty or invalid docs are removed."""

    df = DataFilter()

    docs = [
        {"title": "Valid", "content": "Python testing is great"},
        {"title": "Invalid", "content": ""},
    ]

    results = df.filter(docs)

    assert isinstance(results, list)
    assert len(results) == 1
    assert "Python" in results[0]["content"]


def test_filter_empty_input():
    """Ensure empty input returns empty list."""

    df = DataFilter()

    results = df.filter([])
    assert results == []
