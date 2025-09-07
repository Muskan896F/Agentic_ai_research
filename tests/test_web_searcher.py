# tests/test_web_searcher.py
"""
Unit tests for WebSearcher agent.
We mock API calls so tests don’t hit real search engines.
"""

import pytest
from agents.web_searcher import WebSearcher


def test_search_returns_results(monkeypatch):
    """Ensure search() returns a valid list of results."""

    ws = WebSearcher(api_key="fake_key")

    def fake_call_api(query: str):
        return [
            {"title": "Python Testing", "link": "https://example.com/python"},
            {"title": "Pytest Guide", "link": "https://example.com/pytest"},
        ]

    monkeypatch.setattr(ws, "call_api", fake_call_api)

    results = ws.search("python testing")
    assert isinstance(results, list)
    assert len(results) == 2
    assert "title" in results[0]
    assert "link" in results[0]


def test_search_empty_query(monkeypatch):
    """Ensure empty query returns empty list."""

    ws = WebSearcher(api_key="fake_key")

    def fake_call_api(query: str):
        return []

    monkeypatch.setattr(ws, "call_api", fake_call_api)

    results = ws.search("")
    assert results == []
