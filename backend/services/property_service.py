"""
HomePilot AI — Property Service

Provides property CRUD, search, and favorites management.
Bridges the API layer with the property search tool and database.
"""

from __future__ import annotations

from typing import Any, Optional

from tools.property_search import (
    get_all_properties,
    get_property_by_id,
    MOCK_PROPERTIES,
)
from database.database import get_db
from utils.logger import get_logger
from utils.helpers import format_inr

logger = get_logger(__name__)


def search_properties(
    city: str | None = None,
    budget_min: float | None = None,
    budget_max: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    property_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search properties with filters (direct, non-agent search).

    Returns filtered and formatted property list.
    """
    from tools.property_search import _match_properties

    results = _match_properties(
        budget_min=budget_min,
        budget_max=budget_max,
        city=city,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        property_type=property_type,
    )
    return results


def get_property_detail(property_id: str) -> dict[str, Any] | None:
    """
    Get full property details by ID.

    Checks in-memory mock data first, then database.
    """
    prop = get_property_by_id(property_id)
    if prop:
        return prop

    # Check database
    db = get_db()
    return db.get_property(property_id)


def get_property_history(property_id: str) -> dict[str, Any] | None:
    """Get price history for a property."""
    prop = get_property_by_id(property_id)
    if not prop:
        return None

    from tools.price_history import APPRECIATION_RATES, _generate_price_history

    locality = prop.get("locality", "")
    appreciation = APPRECIATION_RATES.get(locality, 8.0)
    history = _generate_price_history(prop["price"], appreciation)

    return {
        "property_id": property_id,
        "current_price": prop["price"],
        "formatted_price": format_inr(prop["price"]),
        "locality": locality,
        "appreciation_rate": appreciation,
        "price_history": history,
    }


def browse_all_properties() -> list[dict[str, Any]]:
    """Get all properties for browsing."""
    return get_all_properties()
