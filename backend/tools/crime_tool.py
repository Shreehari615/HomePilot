"""
HomePilot AI — Crime Tool

Returns safety scores and crime indices for a given locality.
Uses realistic mock data with crime type breakdowns.
"""

from __future__ import annotations

import random
import time
from typing import Any

from langchain_core.tools import tool

from utils.logger import log_tool_call


# ── Mock Crime/Safety Data ───────────────────────────────────────────────────
# safety_score: 0-100 (higher = safer)
# crime_index: 0-100 (higher = more crime)

LOCALITY_SAFETY: dict[str, dict[str, Any]] = {
    # Mumbai
    "Andheri West": {"safety_score": 72, "crime_index": 28, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Bandra East": {"safety_score": 78, "crime_index": 22, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 3, "cctv_coverage": "Excellent"},
    "Powai": {"safety_score": 85, "crime_index": 15, "crime_types": {"theft": "Very Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Very Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Worli": {"safety_score": 82, "crime_index": 18, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Very Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Kandivali East": {"safety_score": 65, "crime_index": 35, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 1, "cctv_coverage": "Moderate"},
    "Thane West": {"safety_score": 70, "crime_index": 30, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    # Bangalore
    "Whitefield": {"safety_score": 75, "crime_index": 25, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Koramangala": {"safety_score": 73, "crime_index": 27, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Sarjapur Road": {"safety_score": 68, "crime_index": 32, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 1, "cctv_coverage": "Moderate"},
    "Electronic City": {"safety_score": 78, "crime_index": 22, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Indiranagar": {"safety_score": 80, "crime_index": 20, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    # Delhi NCR
    "Dwarka": {"safety_score": 74, "crime_index": 26, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 3, "cctv_coverage": "Good"},
    "Vasant Kunj": {"safety_score": 80, "crime_index": 20, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Noida": {"safety_score": 70, "crime_index": 30, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Gurgaon": {"safety_score": 66, "crime_index": 34, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 2, "cctv_coverage": "Moderate"},
    "Greater Noida": {"safety_score": 62, "crime_index": 38, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Moderate", "vandalism": "Moderate"}, "police_stations_nearby": 1, "cctv_coverage": "Low"},
    # Pune
    "Hinjawadi": {"safety_score": 76, "crime_index": 24, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 1, "cctv_coverage": "Good"},
    "Koregaon Park": {"safety_score": 82, "crime_index": 18, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Baner": {"safety_score": 77, "crime_index": 23, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 1, "cctv_coverage": "Good"},
    "Wakad": {"safety_score": 71, "crime_index": 29, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 1, "cctv_coverage": "Moderate"},
    "Kharadi": {"safety_score": 75, "crime_index": 25, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 1, "cctv_coverage": "Good"},
    # Hyderabad
    "Gachibowli": {"safety_score": 80, "crime_index": 20, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Kompally": {"safety_score": 60, "crime_index": 40, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Moderate", "vandalism": "Moderate"}, "police_stations_nearby": 1, "cctv_coverage": "Low"},
    "Jubilee Hills": {"safety_score": 88, "crime_index": 12, "crime_types": {"theft": "Very Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Very Low"}, "police_stations_nearby": 3, "cctv_coverage": "Excellent"},
    "Kukatpally": {"safety_score": 68, "crime_index": 32, "crime_types": {"theft": "Moderate", "assault": "Low", "burglary": "Low", "vandalism": "Moderate"}, "police_stations_nearby": 2, "cctv_coverage": "Moderate"},
    "Madhapur": {"safety_score": 79, "crime_index": 21, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    # Chennai
    "Besant Nagar": {"safety_score": 83, "crime_index": 17, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Very Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "OMR": {"safety_score": 72, "crime_index": 28, "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
    "Anna Nagar": {"safety_score": 81, "crime_index": 19, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    # Kolkata
    "New Town": {"safety_score": 82, "crime_index": 18, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Very Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Excellent"},
    "Salt Lake": {"safety_score": 80, "crime_index": 20, "crime_types": {"theft": "Low", "assault": "Very Low", "burglary": "Low", "vandalism": "Low"}, "police_stations_nearby": 2, "cctv_coverage": "Good"},
}


@tool
def crime_tool(locality: str, city: str = "") -> dict[str, Any]:
    """
    Get safety score and crime index for a locality.

    Args:
        locality: The locality or neighborhood name
        city: The city name for context

    Returns:
        Dictionary with safety_score (0-100, higher=safer),
        crime_index (0-100, higher=more crime), and crime type breakdown.
    """
    start = time.time()

    data = LOCALITY_SAFETY.get(locality, {
        "safety_score": random.randint(55, 80),
        "crime_index": random.randint(20, 45),
        "crime_types": {"theft": "Low", "assault": "Low", "burglary": "Low", "vandalism": "Low"},
        "police_stations_nearby": random.randint(1, 2),
        "cctv_coverage": "Moderate",
    })

    result = {
        "locality": locality,
        "city": city,
        **data,
    }

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="crime_tool",
        input_data={"locality": locality},
        output_summary=f"Safety: {data['safety_score']}/100, Crime Index: {data['crime_index']}",
        duration_ms=elapsed,
    )

    return result
