"""
HomePilot AI — Helper Utilities

General-purpose helper functions for ID generation, formatting,
data validation, and currency conversion.
"""

from __future__ import annotations

import uuid
import re
from datetime import datetime, timezone
from typing import Any


def generate_id() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate a short 8-character identifier."""
    return uuid.uuid4().hex[:8]


def now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def now_timestamp() -> float:
    """Return the current UTC timestamp as a float."""
    return datetime.now(timezone.utc).timestamp()


def format_inr(amount: float) -> str:
    """
    Format a number as Indian Rupees with lakh/crore notation.

    Examples:
        >>> format_inr(7500000)
        '₹75.00 Lakh'
        >>> format_inr(15000000)
        '₹1.50 Crore'
        >>> format_inr(500000)
        '₹5.00 Lakh'
    """
    if amount >= 1_00_00_000:  # 1 crore = 10 million
        return f"₹{amount / 1_00_00_000:.2f} Crore"
    elif amount >= 1_00_000:  # 1 lakh = 100,000
        return f"₹{amount / 1_00_000:.2f} Lakh"
    else:
        return f"₹{amount:,.0f}"


def parse_budget(text: str) -> dict[str, float | None]:
    """
    Parse a budget string into min/max values in INR.

    Understands formats like:
        "80 lakh", "1.5 crore", "50-80 lakh", "under 1 crore"

    Returns:
        Dictionary with 'min' and 'max' keys (values in raw INR).
    """
    text = text.lower().strip()
    result: dict[str, float | None] = {"min": None, "max": None}

    # Handle "under X" / "below X" / "less than X"
    under_match = re.search(
        r'(?:under|below|less\s+than|upto|up\s+to)\s+([\d.]+)\s*(lakh|lac|crore|cr)',
        text,
    )
    if under_match:
        value = float(under_match.group(1))
        unit = under_match.group(2)
        multiplier = 1_00_00_000 if unit in ("crore", "cr") else 1_00_000
        result["max"] = value * multiplier
        return result

    # Handle range "X-Y lakh/crore"
    range_match = re.search(
        r'([\d.]+)\s*[-–to]+\s*([\d.]+)\s*(lakh|lac|crore|cr)',
        text,
    )
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        unit = range_match.group(3)
        multiplier = 1_00_00_000 if unit in ("crore", "cr") else 1_00_000
        result["min"] = low * multiplier
        result["max"] = high * multiplier
        return result

    # Handle single value "X lakh/crore"
    single_match = re.search(r'([\d.]+)\s*(lakh|lac|crore|cr)', text)
    if single_match:
        value = float(single_match.group(1))
        unit = single_match.group(2)
        multiplier = 1_00_00_000 if unit in ("crore", "cr") else 1_00_000
        result["max"] = value * multiplier
        return result

    return result


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))


def normalize_score(
    value: float,
    min_val: float,
    max_val: float,
    invert: bool = False,
) -> float:
    """
    Normalize a value to the 0-1 range.

    Args:
        value:   Raw value to normalize.
        min_val: Minimum expected value.
        max_val: Maximum expected value.
        invert:  If True, higher raw values produce lower scores
                 (useful for crime index where lower is better).

    Returns:
        Normalized float between 0.0 and 1.0.
    """
    if max_val == min_val:
        return 0.5
    normalized = (value - min_val) / (max_val - min_val)
    normalized = clamp(normalized)
    return 1.0 - normalized if invert else normalized


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely traverse nested dictionaries.

    Args:
        data:    Root dictionary.
        *keys:   Sequence of keys to traverse.
        default: Value to return if any key is missing.

    Returns:
        The value at the nested key path, or default.
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current


def truncate(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length, appending '…' if trimmed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"
