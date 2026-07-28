"""Unit test suite for ADK Agent tools."""

import pytest
from app.tools import analyze_user_query, safe_calculator


def test_analyze_user_query_success():
    result = analyze_user_query("What is the weather in San Francisco?", max_results=3)
    assert result["status"] == "success"
    assert result["error"] is None
    assert result["data"]["original_query"] == "What is the weather in San Francisco?"
    assert len(result["data"]["keywords"]) <= 3


def test_analyze_user_query_empty_error():
    result = analyze_user_query("")
    assert result["status"] == "error"
    assert result["data"] is None
    assert "cannot be empty" in result["error"]


def test_safe_calculator_success():
    result = safe_calculator("15 * 4 + 10")
    assert result["status"] == "success"
    assert result["error"] is None
    assert result["data"]["result"] == 70


def test_safe_calculator_invalid_chars():
    result = safe_calculator("import os; os.system('ls')")
    assert result["status"] == "error"
    assert result["data"] is None
    assert "Invalid characters" in result["error"]
