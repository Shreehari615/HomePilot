"""
HomePilot AI — Price History Tool

Returns historical price data and appreciation rates for properties.
Generates realistic 5-year monthly price history with trends.
"""

from __future__ import annotations

import math
import random
import time
from typing import Any

from langchain_core.tools import tool

from utils.logger import log_tool_call


# ── Appreciation Rates by Locality (annual %) ────────────────────────────────

APPRECIATION_RATES: dict[str, float] = {
    # Mumbai
    "Andheri West": 7.5,
    "Bandra East": 8.2,
    "Powai": 9.0,
    "Worli": 10.5,
    "Kandivali East": 5.5,
    "Thane West": 8.0,
    # Bangalore
    "Whitefield": 9.5,
    "Koramangala": 8.8,
    "Sarjapur Road": 12.0,
    "Electronic City": 7.5,
    "Indiranagar": 9.0,
    # Delhi NCR
    "Dwarka": 6.5,
    "Vasant Kunj": 7.0,
    "Noida": 8.5,
    "Gurgaon": 7.8,
    "Greater Noida": 10.0,
    # Pune
    "Hinjawadi": 11.0,
    "Koregaon Park": 7.5,
    "Baner": 9.5,
    "Wakad": 10.5,
    "Kharadi": 11.5,
    # Hyderabad
    "Gachibowli": 12.5,
    "Kompally": 14.0,
    "Jubilee Hills": 8.0,
    "Kukatpally": 9.0,
    "Madhapur": 11.0,
    # Chennai
    "Besant Nagar": 6.5,
    "OMR": 10.0,
    "Anna Nagar": 7.0,
    # Kolkata
    "New Town": 11.0,
    "Salt Lake": 7.5,
}


def _generate_price_history(
    current_price: float,
    appreciation_rate: float,
    years: int = 5,
) -> list[dict[str, Any]]:
    """
    Generate realistic monthly price history going backwards from current price.

    Uses the appreciation rate with slight monthly variation to create
    realistic-looking data.
    """
    history = []
    monthly_rate = appreciation_rate / 100 / 12

    price = current_price
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    # Generate points going backwards
    data_points = []
    for month_offset in range(years * 12, -1, -1):
        year = 2026 - (month_offset // 12)
        month_idx = (12 - (month_offset % 12)) % 12
        if month_offset == 0:
            data_points.append({
                "date": f"{months[month_idx]} {year}",
                "price": round(current_price),
                "month_num": 0,
            })
        else:
            # Work backwards with some noise
            factor = 1 + monthly_rate + random.uniform(-0.003, 0.003)
            price = price / factor
            data_points.append({
                "date": f"{months[month_idx]} {year}",
                "price": round(price),
                "month_num": -month_offset,
            })

    # Sort chronologically
    data_points.sort(key=lambda x: x["month_num"])

    # Return only date and price
    return [{"date": dp["date"], "price": dp["price"]} for dp in data_points]


@tool
def price_history_tool(
    property_id: str,
    current_price: float = 0,
    locality: str = "",
) -> dict[str, Any]:
    """
    Get historical price data and appreciation rate for a property.

    Args:
        property_id: The property ID to get history for
        current_price: Current property price in INR
        locality: Property locality for appreciation rate lookup

    Returns:
        Dictionary with price_history (5 years monthly), appreciation_rate,
        price_5y_ago, and total_appreciation.
    """
    start = time.time()

    appreciation = APPRECIATION_RATES.get(locality, random.uniform(6.0, 12.0))

    if current_price <= 0:
        current_price = 10000000  # Default 1 crore

    history = _generate_price_history(current_price, appreciation)
    price_5y_ago = history[0]["price"] if history else current_price
    total_appreciation = ((current_price - price_5y_ago) / price_5y_ago) * 100

    result = {
        "property_id": property_id,
        "locality": locality,
        "current_price": current_price,
        "appreciation_rate_annual": round(appreciation, 1),
        "price_history": history,
        "price_5y_ago": price_5y_ago,
        "total_appreciation_5y": round(total_appreciation, 1),
    }

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="price_history",
        input_data={"property_id": property_id, "locality": locality},
        output_summary=f"Appreciation: {appreciation:.1f}%/yr, 5yr total: {total_appreciation:.1f}%",
        duration_ms=elapsed,
    )

    return result
