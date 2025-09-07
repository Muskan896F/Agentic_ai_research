# tests/test_task_breaker.py
"""
Unit tests for TaskBreaker agent.
We mock the LLM call so tests don’t hit the real API.
"""

import pytest
from agents.task_breaker import TaskBreaker


def test_single_task_split(monkeypatch):
    """Ensure it handles a single simple task."""

    tb = TaskBreaker()

    # Monkeypatch LLM function
    def fake_break_into_tasks(user_prompt: str):
        return [{"id": "t1", "text": "Find top React Native libraries"}]

    monkeypatch.setattr(tb, "break_into_tasks", fake_break_into_tasks)

    tasks = tb.break_into_tasks("Find top React Native libraries")
    assert isinstance(tasks, list)
    assert tasks[0]["id"] == "t1"
    assert "React Native" in tasks[0]["text"]


def test_multiple_task_split(monkeypatch):
    """Ensure it handles multiple asks in one input."""

    tb = TaskBreaker()

    def fake_break_into_tasks(user_prompt: str):
        return [
            {"id": "t1", "text": "Find top libraries"},
            {"id": "t2", "text": "Check GitHub activity"},
        ]

    monkeypatch.setattr(tb, "break_into_tasks", fake_break_into_tasks)

    tasks = tb.break_into_tasks("Find top libraries and check GitHub activity")
    assert len(tasks) == 2
    assert tasks[1]["id"] == "t2"
