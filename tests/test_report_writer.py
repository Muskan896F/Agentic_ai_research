# tests/test_report_writer.py
"""
Unit tests for ReportWriter agent.
We use tmp_path fixture so tests don’t write to real reports folder.
"""

import pytest
from agents.report_writer import ReportWriter


def test_write_report_creates_file(tmp_path):
    """Ensure report is written as a file."""

    rw = ReportWriter(output_dir=tmp_path)

    file_path = rw.write_report("test_topic", "# Test Report")

    assert file_path.exists()
    assert file_path.suffix == ".md"
    assert "test_topic" in file_path.name
    assert file_path.read_text().startswith("# Test Report")


def test_write_empty_report(tmp_path):
    """Ensure empty content still creates a file."""

    rw = ReportWriter(output_dir=tmp_path)

    file_path = rw.write_report("empty_topic", "")
    assert file_path.exists()
    assert file_path.read_text() == ""
