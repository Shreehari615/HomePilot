"""
HomePilot AI — Neighborhood Tool

Returns neighborhood amenities data including parks, restaurants,
supermarkets, and walkability scores.
"""

from __future__ import annotations

import random
import time
from typing import Any

from langchain_core.tools import tool

from utils.logger import log_tool_call


# ── Mock Neighborhood Data ───────────────────────────────────────────────────

LOCALITY_NEIGHBORHOOD: dict[str, dict[str, Any]] = {
    # Mumbai
    "Andheri West": {
        "parks": [{"name": "Joggers Park", "distance_km": 1.5}, {"name": "Lokhandwala Garden", "distance_km": 0.5}],
        "restaurants": [{"name": "Hakkasan", "distance_km": 1.0, "cuisine": "Chinese"}, {"name": "Bademiya", "distance_km": 2.0, "cuisine": "Mughlai"}, {"name": "Starbucks", "distance_km": 0.3, "cuisine": "Cafe"}, {"name": "Pizza Express", "distance_km": 0.8, "cuisine": "Italian"}],
        "supermarkets": [{"name": "D-Mart", "distance_km": 1.0}, {"name": "Nature's Basket", "distance_km": 0.5}, {"name": "Star Bazaar", "distance_km": 1.5}],
        "walkability_score": 78,
        "nightlife_score": 75,
        "green_cover": "Moderate",
    },
    "Bandra East": {
        "parks": [{"name": "Bandra Reclamation Promenade", "distance_km": 1.5}, {"name": "Carter Road Promenade", "distance_km": 2.0}],
        "restaurants": [{"name": "Bastian", "distance_km": 2.0, "cuisine": "Seafood"}, {"name": "Pali Village Cafe", "distance_km": 2.5, "cuisine": "Continental"}, {"name": "Lucky Biryani", "distance_km": 1.0, "cuisine": "Mughlai"}],
        "supermarkets": [{"name": "Foodhall", "distance_km": 2.0}, {"name": "Reliance Fresh", "distance_km": 0.8}],
        "walkability_score": 72,
        "nightlife_score": 85,
        "green_cover": "Low",
    },
    "Powai": {
        "parks": [{"name": "Powai Lake Garden", "distance_km": 0.5}, {"name": "Hiranandani Gardens Park", "distance_km": 0.3}],
        "restaurants": [{"name": "Galleria Food Court", "distance_km": 0.5, "cuisine": "Multi"}, {"name": "Soda Bottle Opener", "distance_km": 1.0, "cuisine": "Parsi"}, {"name": "Starbucks Powai", "distance_km": 0.5, "cuisine": "Cafe"}],
        "supermarkets": [{"name": "Big Bazaar", "distance_km": 1.0}, {"name": "Nature's Basket Powai", "distance_km": 0.5}, {"name": "D-Mart", "distance_km": 2.0}],
        "walkability_score": 82,
        "nightlife_score": 55,
        "green_cover": "High",
    },
    "Worli": {
        "parks": [{"name": "Worli Sea Face", "distance_km": 0.5}, {"name": "Worli Fort Garden", "distance_km": 1.0}],
        "restaurants": [{"name": "Ziya", "distance_km": 1.0, "cuisine": "Indian"}, {"name": "Wasabi", "distance_km": 1.5, "cuisine": "Japanese"}, {"name": "Li Bai", "distance_km": 2.0, "cuisine": "Chinese"}],
        "supermarkets": [{"name": "Gourmet West", "distance_km": 1.0}, {"name": "Nature's Basket", "distance_km": 1.5}],
        "walkability_score": 70,
        "nightlife_score": 80,
        "green_cover": "Moderate",
    },
    # Bangalore
    "Whitefield": {
        "parks": [{"name": "AECS Layout Park", "distance_km": 1.0}, {"name": "Nallurhalli Park", "distance_km": 1.5}],
        "restaurants": [{"name": "Windmills Craftworks", "distance_km": 2.0, "cuisine": "Continental"}, {"name": "Toscano", "distance_km": 1.5, "cuisine": "Italian"}, {"name": "Meghana Foods", "distance_km": 1.0, "cuisine": "South Indian"}],
        "supermarkets": [{"name": "Spar Hypermarket", "distance_km": 1.5}, {"name": "More Supermarket", "distance_km": 0.8}],
        "walkability_score": 65,
        "nightlife_score": 50,
        "green_cover": "Moderate",
    },
    "Koramangala": {
        "parks": [{"name": "Koramangala Club Park", "distance_km": 0.5}, {"name": "National Games Village Park", "distance_km": 1.5}],
        "restaurants": [{"name": "Truffles", "distance_km": 0.3, "cuisine": "Continental"}, {"name": "Meghana Foods", "distance_km": 0.5, "cuisine": "Biryani"}, {"name": "The Humming Tree", "distance_km": 1.0, "cuisine": "Cafe"}, {"name": "Toit", "distance_km": 0.8, "cuisine": "Brewery"}],
        "supermarkets": [{"name": "Star Bazaar", "distance_km": 0.5}, {"name": "Namdhari Fresh", "distance_km": 0.8}, {"name": "Big Basket Hub", "distance_km": 1.0}],
        "walkability_score": 80,
        "nightlife_score": 90,
        "green_cover": "Moderate",
    },
    "Indiranagar": {
        "parks": [{"name": "Indiranagar Club", "distance_km": 0.5}],
        "restaurants": [{"name": "Toit Brewery", "distance_km": 1.0, "cuisine": "Brewery"}, {"name": "Smoke House Deli", "distance_km": 0.5, "cuisine": "Continental"}, {"name": "Nagarjuna", "distance_km": 0.8, "cuisine": "Andhra"}, {"name": "Corner House", "distance_km": 0.3, "cuisine": "Desserts"}],
        "supermarkets": [{"name": "Foodworld", "distance_km": 0.3}, {"name": "Fresh @", "distance_km": 0.8}],
        "walkability_score": 85,
        "nightlife_score": 92,
        "green_cover": "Moderate",
    },
    # Delhi NCR
    "Dwarka": {
        "parks": [{"name": "Dwarka Sector 10 Park", "distance_km": 0.5}, {"name": "Bharat Vandana Udyan", "distance_km": 2.0}],
        "restaurants": [{"name": "Barbeque Nation", "distance_km": 1.5, "cuisine": "BBQ"}, {"name": "Haldirams", "distance_km": 1.0, "cuisine": "Indian"}],
        "supermarkets": [{"name": "Big Bazaar", "distance_km": 1.5}, {"name": "Spencer's", "distance_km": 2.0}],
        "walkability_score": 68,
        "nightlife_score": 35,
        "green_cover": "High",
    },
    "Vasant Kunj": {
        "parks": [{"name": "Vasant Kunj Biodiversity Park", "distance_km": 1.0}, {"name": "Deer Park", "distance_km": 3.0}],
        "restaurants": [{"name": "Indian Accent", "distance_km": 3.0, "cuisine": "Indian"}, {"name": "Diva", "distance_km": 2.0, "cuisine": "Italian"}],
        "supermarkets": [{"name": "Le Marche", "distance_km": 1.0}, {"name": "Needs Supermarket", "distance_km": 1.5}],
        "walkability_score": 55,
        "nightlife_score": 60,
        "green_cover": "High",
    },
    # Pune
    "Koregaon Park": {
        "parks": [{"name": "Osho Garden", "distance_km": 0.5}, {"name": "Empress Garden", "distance_km": 2.0}],
        "restaurants": [{"name": "German Bakery", "distance_km": 0.3, "cuisine": "Cafe"}, {"name": "Malaka Spice", "distance_km": 0.5, "cuisine": "Asian"}, {"name": "ABC Farms", "distance_km": 3.0, "cuisine": "Continental"}],
        "supermarkets": [{"name": "Dorabjee's", "distance_km": 0.8}, {"name": "Star Bazaar", "distance_km": 1.5}],
        "walkability_score": 82,
        "nightlife_score": 88,
        "green_cover": "High",
    },
    # Hyderabad
    "Jubilee Hills": {
        "parks": [{"name": "KBR National Park", "distance_km": 1.5}, {"name": "Lotus Pond", "distance_km": 2.0}],
        "restaurants": [{"name": "Olive Bistro", "distance_km": 1.0, "cuisine": "Continental"}, {"name": "Jewel of Nizam", "distance_km": 2.0, "cuisine": "Hyderabadi"}, {"name": "Flechazo", "distance_km": 0.5, "cuisine": "Spanish"}],
        "supermarkets": [{"name": "Ratnadeep", "distance_km": 0.5}, {"name": "More Megastore", "distance_km": 1.5}],
        "walkability_score": 70,
        "nightlife_score": 82,
        "green_cover": "High",
    },
    "Gachibowli": {
        "parks": [{"name": "Gachibowli Stadium Park", "distance_km": 1.0}],
        "restaurants": [{"name": "Ohri's", "distance_km": 1.5, "cuisine": "Multi"}, {"name": "Minerva Grand", "distance_km": 2.0, "cuisine": "South Indian"}],
        "supermarkets": [{"name": "Ratnadeep", "distance_km": 1.0}, {"name": "D-Mart", "distance_km": 2.0}],
        "walkability_score": 62,
        "nightlife_score": 50,
        "green_cover": "Moderate",
    },
}


def _generate_default_neighborhood(locality: str) -> dict[str, Any]:
    """Generate default neighborhood data for unknown localities."""
    return {
        "parks": [{"name": f"{locality} Central Park", "distance_km": round(random.uniform(0.5, 2.0), 1)}],
        "restaurants": [
            {"name": f"{locality} Cafe", "distance_km": round(random.uniform(0.3, 1.5), 1), "cuisine": "Multi"},
            {"name": f"{locality} Bistro", "distance_km": round(random.uniform(0.5, 2.0), 1), "cuisine": "Continental"},
        ],
        "supermarkets": [{"name": "Local Supermarket", "distance_km": round(random.uniform(0.5, 2.0), 1)}],
        "walkability_score": random.randint(50, 80),
        "nightlife_score": random.randint(30, 70),
        "green_cover": random.choice(["Low", "Moderate", "High"]),
    }


@tool
def neighborhood_tool(locality: str, city: str = "") -> dict[str, Any]:
    """
    Get neighborhood amenities: parks, restaurants, supermarkets, walkability.

    Args:
        locality: The locality or neighborhood name
        city: The city name for context

    Returns:
        Dictionary with parks, restaurants, supermarkets, walkability_score,
        nightlife_score, and green_cover.
    """
    start = time.time()

    data = LOCALITY_NEIGHBORHOOD.get(
        locality, _generate_default_neighborhood(locality)
    )

    result = {
        "locality": locality,
        "city": city,
        "parks": data["parks"],
        "parks_count": len(data["parks"]),
        "restaurants": data["restaurants"],
        "restaurants_count": len(data["restaurants"]),
        "supermarkets": data["supermarkets"],
        "supermarkets_count": len(data["supermarkets"]),
        "walkability_score": data["walkability_score"],
        "nightlife_score": data["nightlife_score"],
        "green_cover": data["green_cover"],
    }

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="neighborhood",
        input_data={"locality": locality},
        output_summary=f"Walkability: {data['walkability_score']}/100, {len(data['restaurants'])} restaurants",
        duration_ms=elapsed,
    )

    return result
