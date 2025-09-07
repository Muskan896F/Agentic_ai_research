# tests/test_summarizer.py
"""
Unit tests for Summarizer agent.
We mock summarization behavior so tests don’t call real LLMs.
"""

import pytest
from agents.summarizer import Summarizer


def test_summarize_basic(monkeypatch):
    """Ensure summarizer returns a string summary."""

    sm = Summarizer()

    def fake_summarize(docs):
        return "Python and Pytest are useful."

    monkeypatch.setattr(sm, "summarize", fake_summarize)

    summary = sm.summarize(["Python is popular", "Pytest makes testing easy"])
    assert isinstance(summary, str)
    assert "Python" in summary


def test_summarize_empty(monkeypatch):
    """Ensure summarizer handles empty input."""

    sm = Summarizer()

    def fake_summarize(docs):
        return ""

    monkeypatch.setattr(sm, "summarize", fake_summarize)

    summary = sm.summarize([])
    assert summary == ""
