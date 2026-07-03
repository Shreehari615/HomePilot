"""
HomePilot AI — Helper Utility Tests

Tests for budget parsing, INR formatting, score normalization, and other helpers.
"""

import pytest
from utils.helpers import (
    format_inr,
    parse_budget,
    normalize_score,
    clamp,
    safe_get,
    truncate,
    generate_id,
    generate_short_id,
)


class TestFormatINR:
    def test_crore(self):
        assert format_inr(15000000) == "₹1.50 Crore"

    def test_lakh(self):
        assert format_inr(7500000) == "₹75.00 Lakh"

    def test_small_amount(self):
        assert format_inr(50000) == "₹50,000"

    def test_one_crore(self):
        assert format_inr(10000000) == "₹1.00 Crore"


class TestParseBudget:
    def test_under_lakh(self):
        result = parse_budget("under 80 lakh")
        assert result["max"] == 8000000

    def test_crore(self):
        result = parse_budget("1.5 crore")
        assert result["max"] == 15000000

    def test_range_lakh(self):
        result = parse_budget("50-80 lakh")
        assert result["min"] == 5000000
        assert result["max"] == 8000000

    def test_no_budget(self):
        result = parse_budget("some random text")
        assert result["min"] is None
        assert result["max"] is None


class TestNormalize:
    def test_mid_value(self):
        assert normalize_score(5, 0, 10) == 0.5

    def test_min_value(self):
        assert normalize_score(0, 0, 10) == 0.0

    def test_max_value(self):
        assert normalize_score(10, 0, 10) == 1.0

    def test_inverted(self):
        assert normalize_score(0, 0, 10, invert=True) == 1.0
        assert normalize_score(10, 0, 10, invert=True) == 0.0

    def test_equal_min_max(self):
        assert normalize_score(5, 5, 5) == 0.5


class TestClamp:
    def test_within_range(self):
        assert clamp(0.5) == 0.5

    def test_below_min(self):
        assert clamp(-0.5) == 0.0

    def test_above_max(self):
        assert clamp(1.5) == 1.0


class TestSafeGet:
    def test_simple(self):
        assert safe_get({"a": 1}, "a") == 1

    def test_nested(self):
        assert safe_get({"a": {"b": {"c": 3}}}, "a", "b", "c") == 3

    def test_missing_key(self):
        assert safe_get({"a": 1}, "b", default="nope") == "nope"


class TestTruncate:
    def test_short_text(self):
        assert truncate("hello", 10) == "hello"

    def test_long_text(self):
        result = truncate("a" * 300, 200)
        assert len(result) == 200
        assert result.endswith("…")


class TestGenerateId:
    def test_unique(self):
        assert generate_id() != generate_id()

    def test_short_id_length(self):
        assert len(generate_short_id()) == 8
