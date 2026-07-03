"""
HomePilot AI — Google Maps Tool

Provides commute time estimates, nearby metro stations, hospitals,
and shopping centers for a given property location. Uses realistic
mock data keyed by locality.
"""

from __future__ import annotations

import random
import time
from typing import Any, Optional

from langchain_core.tools import tool

from utils.logger import log_tool_call


# ── Mock Location Data ───────────────────────────────────────────────────────

LOCALITY_DATA: dict[str, dict[str, Any]] = {
    # Mumbai
    "Andheri West": {
        "metro": [
            {"name": "Andheri Metro Station", "distance_km": 0.8, "line": "Blue Line"},
            {"name": "D.N. Nagar Metro Station", "distance_km": 1.2, "line": "Blue Line"},
        ],
        "hospitals": [
            {"name": "Kokilaben Dhirubhai Ambani Hospital", "distance_km": 2.5, "rating": 4.5},
            {"name": "HiranandaniHospital", "distance_km": 3.1, "rating": 4.3},
        ],
        "shopping": [
            {"name": "Infiniti Mall", "distance_km": 0.5, "type": "Mall"},
            {"name": "Lokhandwala Market", "distance_km": 0.3, "type": "Market"},
        ],
        "commute_cbd_min": 45,
    },
    "Bandra East": {
        "metro": [{"name": "Bandra Metro Station", "distance_km": 0.6, "line": "Blue Line"}],
        "hospitals": [
            {"name": "Lilavati Hospital", "distance_km": 2.0, "rating": 4.6},
            {"name": "Holy Family Hospital", "distance_km": 1.5, "rating": 4.2},
        ],
        "shopping": [
            {"name": "BKC Mall", "distance_km": 1.5, "type": "Mall"},
            {"name": "Hill Road Market", "distance_km": 2.0, "type": "Market"},
        ],
        "commute_cbd_min": 30,
    },
    "Powai": {
        "metro": [{"name": "Saki Naka Metro Station", "distance_km": 3.5, "line": "Blue Line"}],
        "hospitals": [
            {"name": "Hiranandani Hospital", "distance_km": 0.8, "rating": 4.4},
            {"name": "Fortis Hospital", "distance_km": 4.0, "rating": 4.3},
        ],
        "shopping": [
            {"name": "Haiko Mall", "distance_km": 1.0, "type": "Mall"},
            {"name": "Powai Plaza", "distance_km": 0.5, "type": "Market"},
        ],
        "commute_cbd_min": 50,
    },
    "Worli": {
        "metro": [{"name": "Worli Metro Station", "distance_km": 0.5, "line": "Line 3"}],
        "hospitals": [
            {"name": "Breach Candy Hospital", "distance_km": 3.0, "rating": 4.7},
            {"name": "Jaslok Hospital", "distance_km": 4.0, "rating": 4.5},
        ],
        "shopping": [
            {"name": "Atria Mall", "distance_km": 1.5, "type": "Mall"},
            {"name": "Phoenix Mills", "distance_km": 2.0, "type": "Mall"},
        ],
        "commute_cbd_min": 20,
    },
    "Kandivali East": {
        "metro": [{"name": "Kandivali Metro Station", "distance_km": 1.5, "line": "Metro Line 7"}],
        "hospitals": [{"name": "Shatabdi Hospital", "distance_km": 1.0, "rating": 3.8}],
        "shopping": [{"name": "Raghuleela Mall", "distance_km": 2.0, "type": "Mall"}],
        "commute_cbd_min": 65,
    },
    "Thane West": {
        "metro": [{"name": "Thane Metro Station (Upcoming)", "distance_km": 2.0, "line": "Metro Line 4"}],
        "hospitals": [
            {"name": "Jupiter Hospital", "distance_km": 1.5, "rating": 4.3},
            {"name": "Bethany Hospital", "distance_km": 2.5, "rating": 4.0},
        ],
        "shopping": [
            {"name": "Viviana Mall", "distance_km": 1.0, "type": "Mall"},
            {"name": "Korum Mall", "distance_km": 3.0, "type": "Mall"},
        ],
        "commute_cbd_min": 55,
    },
    # Bangalore
    "Whitefield": {
        "metro": [{"name": "Whitefield Metro Station", "distance_km": 1.0, "line": "Purple Line"}],
        "hospitals": [
            {"name": "Columbia Asia Hospital", "distance_km": 1.5, "rating": 4.2},
            {"name": "Manipal Hospital", "distance_km": 3.0, "rating": 4.5},
        ],
        "shopping": [
            {"name": "Phoenix Marketcity", "distance_km": 2.0, "type": "Mall"},
            {"name": "VR Bengaluru", "distance_km": 1.5, "type": "Mall"},
        ],
        "commute_cbd_min": 55,
    },
    "Koramangala": {
        "metro": [{"name": "HSR Layout Metro (Upcoming)", "distance_km": 2.5, "line": "Yellow Line"}],
        "hospitals": [
            {"name": "Apollo Hospital", "distance_km": 2.0, "rating": 4.6},
            {"name": "St. John's Hospital", "distance_km": 3.0, "rating": 4.4},
        ],
        "shopping": [
            {"name": "Forum Mall", "distance_km": 1.0, "type": "Mall"},
            {"name": "Koramangala BDA Complex", "distance_km": 0.5, "type": "Market"},
        ],
        "commute_cbd_min": 25,
    },
    "Sarjapur Road": {
        "metro": [{"name": "Sarjapur Road Metro (Upcoming)", "distance_km": 4.0, "line": "Yellow Line"}],
        "hospitals": [{"name": "Motherhood Hospital", "distance_km": 2.0, "rating": 4.1}],
        "shopping": [{"name": "Total Mall", "distance_km": 1.5, "type": "Mall"}],
        "commute_cbd_min": 60,
    },
    "Electronic City": {
        "metro": [{"name": "Electronic City Metro (Upcoming)", "distance_km": 3.0, "line": "Yellow Line"}],
        "hospitals": [{"name": "Narayana Health", "distance_km": 2.5, "rating": 4.5}],
        "shopping": [{"name": "Gopalan Innovation Mall", "distance_km": 1.0, "type": "Mall"}],
        "commute_cbd_min": 50,
    },
    "Indiranagar": {
        "metro": [{"name": "Indiranagar Metro Station", "distance_km": 0.5, "line": "Purple Line"}],
        "hospitals": [{"name": "Manipal Hospital", "distance_km": 3.0, "rating": 4.5}],
        "shopping": [
            {"name": "1 MG Mall", "distance_km": 2.0, "type": "Mall"},
            {"name": "100 Feet Road Shops", "distance_km": 0.3, "type": "Market"},
        ],
        "commute_cbd_min": 20,
    },
    # Delhi NCR
    "Dwarka": {
        "metro": [
            {"name": "Dwarka Sector 21 Metro", "distance_km": 0.8, "line": "Blue Line"},
            {"name": "Dwarka Mor Metro", "distance_km": 1.5, "line": "Blue Line"},
        ],
        "hospitals": [{"name": "Venkateshwar Hospital", "distance_km": 2.0, "rating": 4.2}],
        "shopping": [{"name": "Vegas Mall", "distance_km": 1.5, "type": "Mall"}],
        "commute_cbd_min": 40,
    },
    "Vasant Kunj": {
        "metro": [{"name": "Chattarpur Metro", "distance_km": 3.0, "line": "Yellow Line"}],
        "hospitals": [
            {"name": "Fortis Hospital", "distance_km": 2.5, "rating": 4.5},
            {"name": "Max Hospital", "distance_km": 4.0, "rating": 4.4},
        ],
        "shopping": [
            {"name": "Ambience Mall", "distance_km": 3.0, "type": "Mall"},
            {"name": "DLF Promenade", "distance_km": 2.0, "type": "Mall"},
        ],
        "commute_cbd_min": 35,
    },
    "Noida": {
        "metro": [{"name": "Noida Sector 137 Metro", "distance_km": 2.0, "line": "Blue Line"}],
        "hospitals": [{"name": "Max Hospital Noida", "distance_km": 5.0, "rating": 4.3}],
        "shopping": [{"name": "DLF Mall of India", "distance_km": 8.0, "type": "Mall"}],
        "commute_cbd_min": 60,
    },
    "Gurgaon": {
        "metro": [{"name": "HUDA City Centre Metro", "distance_km": 5.0, "line": "Yellow Line"}],
        "hospitals": [{"name": "Medanta Hospital", "distance_km": 3.0, "rating": 4.7}],
        "shopping": [{"name": "Ambience Mall Gurgaon", "distance_km": 4.0, "type": "Mall"}],
        "commute_cbd_min": 55,
    },
    "Greater Noida": {
        "metro": [{"name": "Aqua Line Stations", "distance_km": 3.0, "line": "Aqua Line"}],
        "hospitals": [{"name": "Yatharth Hospital", "distance_km": 2.0, "rating": 4.0}],
        "shopping": [{"name": "Grand Venice Mall", "distance_km": 5.0, "type": "Mall"}],
        "commute_cbd_min": 75,
    },
    # Pune
    "Hinjawadi": {
        "metro": [{"name": "Hinjawadi Metro (Upcoming)", "distance_km": 2.0, "line": "Purple Line"}],
        "hospitals": [{"name": "Aditya Birla Hospital", "distance_km": 3.0, "rating": 4.3}],
        "shopping": [{"name": "Xion Mall", "distance_km": 1.5, "type": "Mall"}],
        "commute_cbd_min": 50,
    },
    "Koregaon Park": {
        "metro": [{"name": "Pune Metro Station (Upcoming)", "distance_km": 3.5, "line": "Aqua Line"}],
        "hospitals": [{"name": "Jehangir Hospital", "distance_km": 2.5, "rating": 4.5}],
        "shopping": [{"name": "Phoenix Marketcity Pune", "distance_km": 4.0, "type": "Mall"}],
        "commute_cbd_min": 15,
    },
    "Baner": {
        "metro": [{"name": "Baner Metro (Upcoming)", "distance_km": 1.5, "line": "Purple Line"}],
        "hospitals": [{"name": "Jupiter Hospital Pune", "distance_km": 2.0, "rating": 4.2}],
        "shopping": [{"name": "Balewadi High Street", "distance_km": 1.0, "type": "Mall"}],
        "commute_cbd_min": 30,
    },
    "Wakad": {
        "metro": [{"name": "Wakad Metro (Upcoming)", "distance_km": 2.0, "line": "Purple Line"}],
        "hospitals": [{"name": "Lifepoint Hospital", "distance_km": 1.5, "rating": 3.9}],
        "shopping": [{"name": "Westend Mall", "distance_km": 2.0, "type": "Mall"}],
        "commute_cbd_min": 40,
    },
    "Kharadi": {
        "metro": [{"name": "Kharadi Metro (Upcoming)", "distance_km": 2.5, "line": "Purple Line"}],
        "hospitals": [{"name": "Columbia Asia Pune", "distance_km": 1.0, "rating": 4.1}],
        "shopping": [{"name": "Amanora Mall", "distance_km": 2.0, "type": "Mall"}],
        "commute_cbd_min": 25,
    },
    # Hyderabad
    "Gachibowli": {
        "metro": [{"name": "Raidurg Metro Station", "distance_km": 2.0, "line": "Blue Line"}],
        "hospitals": [
            {"name": "Continental Hospital", "distance_km": 1.0, "rating": 4.4},
            {"name": "AIG Hospital", "distance_km": 3.0, "rating": 4.3},
        ],
        "shopping": [{"name": "Inorbit Mall", "distance_km": 2.5, "type": "Mall"}],
        "commute_cbd_min": 35,
    },
    "Kompally": {
        "metro": [{"name": "JBS Metro (Nearest)", "distance_km": 8.0, "line": "Red Line"}],
        "hospitals": [{"name": "KIMS Hospital", "distance_km": 4.0, "rating": 4.1}],
        "shopping": [{"name": "Kompally Market", "distance_km": 1.0, "type": "Market"}],
        "commute_cbd_min": 50,
    },
    "Jubilee Hills": {
        "metro": [{"name": "Jubilee Hills Check Post Metro", "distance_km": 1.0, "line": "Blue Line"}],
        "hospitals": [
            {"name": "Apollo Hospital", "distance_km": 2.0, "rating": 4.7},
            {"name": "CARE Hospital", "distance_km": 3.0, "rating": 4.5},
        ],
        "shopping": [
            {"name": "GVK One Mall", "distance_km": 2.0, "type": "Mall"},
            {"name": "Jubilee Hills Road No 36 Shops", "distance_km": 0.5, "type": "Market"},
        ],
        "commute_cbd_min": 15,
    },
    "Kukatpally": {
        "metro": [{"name": "KPHB Colony Metro", "distance_km": 0.5, "line": "Red Line"}],
        "hospitals": [{"name": "Sunshine Hospital", "distance_km": 1.5, "rating": 4.0}],
        "shopping": [{"name": "Forum Sujana Mall", "distance_km": 1.0, "type": "Mall"}],
        "commute_cbd_min": 30,
    },
    "Madhapur": {
        "metro": [{"name": "Madhapur Metro Station", "distance_km": 0.8, "line": "Blue Line"}],
        "hospitals": [{"name": "Yashoda Hospital", "distance_km": 1.5, "rating": 4.3}],
        "shopping": [{"name": "Inorbit Mall Hyderabad", "distance_km": 1.0, "type": "Mall"}],
        "commute_cbd_min": 25,
    },
    # Chennai
    "Besant Nagar": {
        "metro": [{"name": "Besant Nagar MRTS Station", "distance_km": 0.5, "line": "MRTS"}],
        "hospitals": [{"name": "Apollo Hospital Chennai", "distance_km": 3.0, "rating": 4.6}],
        "shopping": [{"name": "Elliot's Beach Market", "distance_km": 0.5, "type": "Market"}],
        "commute_cbd_min": 25,
    },
    "OMR": {
        "metro": [{"name": "Thoraipakkam MRTS (Upcoming)", "distance_km": 3.0, "line": "Phase 2"}],
        "hospitals": [{"name": "Chettinad Hospital", "distance_km": 2.0, "rating": 4.2}],
        "shopping": [{"name": "Grand Square Mall", "distance_km": 1.5, "type": "Mall"}],
        "commute_cbd_min": 45,
    },
    "Anna Nagar": {
        "metro": [{"name": "Anna Nagar East Metro", "distance_km": 0.8, "line": "Blue Line"}],
        "hospitals": [
            {"name": "SIMS Hospital", "distance_km": 1.5, "rating": 4.4},
            {"name": "Kauvery Hospital", "distance_km": 2.0, "rating": 4.3},
        ],
        "shopping": [{"name": "Anna Nagar Tower Park Market", "distance_km": 0.5, "type": "Market"}],
        "commute_cbd_min": 20,
    },
    # Kolkata
    "New Town": {
        "metro": [{"name": "New Garia Metro (Nearest)", "distance_km": 6.0, "line": "Blue Line"}],
        "hospitals": [{"name": "Tata Medical Center", "distance_km": 2.0, "rating": 4.5}],
        "shopping": [{"name": "City Centre II", "distance_km": 1.0, "type": "Mall"}],
        "commute_cbd_min": 40,
    },
    "Salt Lake": {
        "metro": [{"name": "Salt Lake Sector V Metro", "distance_km": 1.0, "line": "Green Line"}],
        "hospitals": [{"name": "AMRI Hospital", "distance_km": 2.5, "rating": 4.3}],
        "shopping": [{"name": "City Centre Salt Lake", "distance_km": 1.5, "type": "Mall"}],
        "commute_cbd_min": 30,
    },
}


def _get_default_data(locality: str) -> dict[str, Any]:
    """Generate default location data for unknown localities."""
    return {
        "metro": [{"name": f"Nearest Metro to {locality}", "distance_km": round(random.uniform(1.0, 5.0), 1), "line": "Main Line"}],
        "hospitals": [{"name": f"{locality} General Hospital", "distance_km": round(random.uniform(1.0, 4.0), 1), "rating": round(random.uniform(3.5, 4.5), 1)}],
        "shopping": [{"name": f"{locality} Market", "distance_km": round(random.uniform(0.5, 3.0), 1), "type": "Market"}],
        "commute_cbd_min": random.randint(20, 60),
    }


@tool
def google_maps_tool(
    locality: str,
    city: str = "",
) -> dict[str, Any]:
    """
    Get commute times, nearby metro stations, hospitals, and shopping
    centers for a property location.

    Args:
        locality: The locality or neighborhood name (e.g., 'Andheri West', 'Koramangala')
        city: The city name for context

    Returns:
        Dictionary with commute_time_min, nearest_metro, metro_distance_km,
        nearby_hospitals, nearby_shopping data.
    """
    start = time.time()

    data = LOCALITY_DATA.get(locality, _get_default_data(locality))
    metro_list = data["metro"]
    nearest = min(metro_list, key=lambda m: m["distance_km"])

    result = {
        "locality": locality,
        "city": city,
        "commute_time_min": data["commute_cbd_min"],
        "nearest_metro": nearest["name"],
        "metro_distance_km": nearest["distance_km"],
        "metro_stations": metro_list,
        "nearby_hospitals": data["hospitals"],
        "nearby_shopping": data["shopping"],
    }

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="google_maps",
        input_data={"locality": locality, "city": city},
        output_summary=f"Metro: {nearest['name']} ({nearest['distance_km']}km), Commute: {data['commute_cbd_min']}min",
        duration_ms=elapsed,
    )

    return result
