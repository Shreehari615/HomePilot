"""
HomePilot AI — School Tool

Returns nearby schools with ratings, distance, and board information
for a given locality. Uses realistic mock data.
"""

from __future__ import annotations

import random
import time
from typing import Any

from langchain_core.tools import tool

from utils.logger import log_tool_call


# ── Mock School Data ─────────────────────────────────────────────────────────

LOCALITY_SCHOOLS: dict[str, list[dict[str, Any]]] = {
    "Andheri West": [
        {"name": "SVKM International School", "rating": 8.5, "distance_km": 1.2, "board": "IB", "type": "Co-ed"},
        {"name": "Lokhandwala Foundation School", "rating": 7.8, "distance_km": 0.5, "board": "ICSE", "type": "Co-ed"},
        {"name": "Ryan International", "rating": 7.2, "distance_km": 2.0, "board": "CBSE", "type": "Co-ed"},
    ],
    "Bandra East": [
        {"name": "Cathedral & John Connon School", "rating": 9.2, "distance_km": 3.5, "board": "ICSE", "type": "Co-ed"},
        {"name": "St. Stanislaus High School", "rating": 8.0, "distance_km": 2.0, "board": "ICSE", "type": "Boys"},
        {"name": "Arya Vidya Mandir", "rating": 8.5, "distance_km": 2.5, "board": "ICSE", "type": "Co-ed"},
    ],
    "Powai": [
        {"name": "Hiranandani Foundation School", "rating": 8.8, "distance_km": 0.5, "board": "ICSE", "type": "Co-ed"},
        {"name": "Powai English School", "rating": 7.5, "distance_km": 1.0, "board": "SSC", "type": "Co-ed"},
        {"name": "IIT Bombay Campus School", "rating": 8.2, "distance_km": 1.5, "board": "CBSE", "type": "Co-ed"},
    ],
    "Worli": [
        {"name": "Bombay Scottish School", "rating": 8.7, "distance_km": 3.0, "board": "ICSE", "type": "Co-ed"},
        {"name": "Jamnabai Narsee School", "rating": 9.0, "distance_km": 4.0, "board": "ICSE", "type": "Co-ed"},
    ],
    "Whitefield": [
        {"name": "Gopalan International School", "rating": 8.0, "distance_km": 1.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "Inventure Academy", "rating": 8.8, "distance_km": 3.0, "board": "IB", "type": "Co-ed"},
        {"name": "VIBGYOR High", "rating": 7.5, "distance_km": 1.5, "board": "ICSE", "type": "Co-ed"},
    ],
    "Koramangala": [
        {"name": "National Public School", "rating": 9.0, "distance_km": 2.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "Bethany High School", "rating": 8.2, "distance_km": 1.5, "board": "ICSE", "type": "Co-ed"},
        {"name": "Greenwood High", "rating": 8.5, "distance_km": 3.0, "board": "ICSE", "type": "Co-ed"},
    ],
    "Indiranagar": [
        {"name": "Bishop Cotton Boys School", "rating": 8.8, "distance_km": 3.0, "board": "ICSE", "type": "Boys"},
        {"name": "St. Francis Xavier School", "rating": 7.8, "distance_km": 2.0, "board": "ICSE", "type": "Co-ed"},
    ],
    "Dwarka": [
        {"name": "Mount Abu Public School", "rating": 7.5, "distance_km": 1.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "DAV Public School", "rating": 7.8, "distance_km": 1.5, "board": "CBSE", "type": "Co-ed"},
        {"name": "DPS Dwarka", "rating": 8.5, "distance_km": 2.0, "board": "CBSE", "type": "Co-ed"},
    ],
    "Vasant Kunj": [
        {"name": "Sanskriti School", "rating": 9.3, "distance_km": 2.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "The Shri Ram School", "rating": 9.5, "distance_km": 3.5, "board": "CBSE", "type": "Co-ed"},
    ],
    "Gachibowli": [
        {"name": "Oakridge International", "rating": 8.5, "distance_km": 1.5, "board": "IB", "type": "Co-ed"},
        {"name": "Delhi Public School Hyderabad", "rating": 8.0, "distance_km": 2.5, "board": "CBSE", "type": "Co-ed"},
        {"name": "Chirec Public School", "rating": 8.3, "distance_km": 3.0, "board": "CBSE", "type": "Co-ed"},
    ],
    "Jubilee Hills": [
        {"name": "Meridian School", "rating": 8.8, "distance_km": 1.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "Hillside Academy", "rating": 8.5, "distance_km": 1.5, "board": "ICSE", "type": "Co-ed"},
        {"name": "Jubilee Hills Public School", "rating": 8.0, "distance_km": 0.8, "board": "CBSE", "type": "Co-ed"},
    ],
    "Hinjawadi": [
        {"name": "Blue Ridge International School", "rating": 7.5, "distance_km": 2.0, "board": "CBSE", "type": "Co-ed"},
        {"name": "Sanskriti School Pune", "rating": 7.0, "distance_km": 3.0, "board": "CBSE", "type": "Co-ed"},
    ],
    "Koregaon Park": [
        {"name": "Bishops School", "rating": 8.8, "distance_km": 2.0, "board": "ICSE", "type": "Co-ed"},
        {"name": "Symbiosis School", "rating": 8.5, "distance_km": 1.5, "board": "CBSE", "type": "Co-ed"},
    ],
}


def _generate_default_schools(locality: str) -> list[dict[str, Any]]:
    """Generate default school data for unknown localities."""
    boards = ["CBSE", "ICSE", "SSC"]
    return [
        {
            "name": f"{locality} Public School",
            "rating": round(random.uniform(6.5, 8.5), 1),
            "distance_km": round(random.uniform(0.5, 3.0), 1),
            "board": random.choice(boards),
            "type": "Co-ed",
        },
        {
            "name": f"{locality} International Academy",
            "rating": round(random.uniform(7.0, 9.0), 1),
            "distance_km": round(random.uniform(1.0, 4.0), 1),
            "board": "CBSE",
            "type": "Co-ed",
        },
    ]


@tool
def school_tool(locality: str, city: str = "") -> dict[str, Any]:
    """
    Find nearby schools with ratings and distance information.

    Args:
        locality: The locality or neighborhood name
        city: The city name for context

    Returns:
        Dictionary with nearby_schools list, average_rating, and best_school.
    """
    start = time.time()

    schools = LOCALITY_SCHOOLS.get(locality, _generate_default_schools(locality))
    avg_rating = sum(s["rating"] for s in schools) / len(schools) if schools else 0
    best = max(schools, key=lambda s: s["rating"]) if schools else None

    result = {
        "locality": locality,
        "city": city,
        "nearby_schools": schools,
        "school_count": len(schools),
        "average_rating": round(avg_rating, 1),
        "best_school": best,
    }

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="school_tool",
        input_data={"locality": locality},
        output_summary=f"{len(schools)} schools, avg rating {avg_rating:.1f}",
        duration_ms=elapsed,
    )

    return result
