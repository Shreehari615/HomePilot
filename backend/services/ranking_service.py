"""
HomePilot AI — Ranking Service

Deterministic weighted scoring algorithm that ranks properties
based on user priorities. Supports dynamic weight adjustment.
"""

from __future__ import annotations

from typing import Any

from models.schemas import RankingWeights
from utils.helpers import normalize_score, clamp
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_property_scores(
    properties: list[dict[str, Any]],
    weights: RankingWeights,
    preferences: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Score and rank properties using the weighted scoring algorithm.

    Score = Σ(weight_i × normalized_factor_i) × 100

    Args:
        properties: List of enriched property dicts (with tool data).
        weights:    Current ranking weights (must sum to 1.0).
        preferences: User preferences for budget matching.

    Returns:
        Properties sorted by overall_score (descending), each augmented
        with overall_score, score_breakdown, rank, and confidence.
    """
    if not properties:
        return []

    prefs = preferences or {}
    normalized_weights = weights.normalize()
    w = normalized_weights.to_dict()

    scored = []
    for prop in properties:
        breakdown = {}

        # ── Budget Match Score ───────────────────────────────────────────
        budget_score = _calculate_budget_score(prop, prefs)
        breakdown["budget_match"] = round(budget_score, 3)

        # ── Commute Score ────────────────────────────────────────────────
        commute_score = _calculate_commute_score(prop, prefs)
        breakdown["commute"] = round(commute_score, 3)

        # ── School Score ─────────────────────────────────────────────────
        school_score = _calculate_school_score(prop)
        breakdown["school"] = round(school_score, 3)

        # ── Safety Score ─────────────────────────────────────────────────
        safety_score = _calculate_safety_score(prop)
        breakdown["safety"] = round(safety_score, 3)

        # ── Amenities Score ──────────────────────────────────────────────
        amenities_score = _calculate_amenities_score(prop)
        breakdown["amenities"] = round(amenities_score, 3)

        # ── Weighted Total ───────────────────────────────────────────────
        overall = (
            w["budget_match"] * budget_score
            + w["commute"] * commute_score
            + w["school"] * school_score
            + w["safety"] * safety_score
            + w["amenities"] * amenities_score
        ) * 100

        overall = round(clamp(overall, 0, 100), 1)

        # ── Confidence ───────────────────────────────────────────────────
        data_completeness = _calculate_data_completeness(prop)
        confidence = round(clamp(data_completeness * 0.9 + 0.1, 0.1, 0.95), 2)

        prop_scored = {**prop}
        prop_scored["overall_score"] = overall
        prop_scored["score_breakdown"] = breakdown
        prop_scored["confidence"] = confidence
        scored.append(prop_scored)

    # Sort by score descending
    scored.sort(key=lambda p: p["overall_score"], reverse=True)

    # Assign ranks
    for i, prop in enumerate(scored):
        prop["rank"] = i + 1

    logger.info(
        "properties_ranked",
        count=len(scored),
        top_score=scored[0]["overall_score"] if scored else 0,
        weights=w,
    )

    return scored


def _calculate_budget_score(prop: dict, prefs: dict) -> float:
    """
    Score how well the property price matches the user's budget.

    Perfect match (at or under budget) = 1.0
    Over budget = decays proportionally
    """
    price = prop.get("price", 0)
    budget_max = prefs.get("budget_max")
    budget_min = prefs.get("budget_min")

    if not budget_max and not budget_min:
        return 0.7  # No budget specified, neutral score

    if budget_max:
        if price <= budget_max:
            # Under budget — closer to max is better (not wasting budget)
            if budget_min:
                range_size = budget_max - budget_min
                if range_size > 0:
                    return clamp(0.5 + 0.5 * ((price - budget_min) / range_size))
            return 1.0
        else:
            # Over budget — penalize proportionally
            over_pct = (price - budget_max) / budget_max
            return clamp(1.0 - over_pct * 3, 0, 1)

    return 0.7


def _calculate_commute_score(prop: dict, prefs: dict) -> float:
    """Score based on commute time and metro proximity."""
    metro_dist = prop.get("metro_distance_km")
    commute_time = prop.get("commute_time_min")

    score = 0.5  # Default neutral

    if metro_dist is not None:
        # < 0.5km = excellent, > 5km = poor
        metro_score = normalize_score(metro_dist, 0, 5.0, invert=True)
        score = metro_score

    if commute_time is not None:
        max_commute = prefs.get("max_commute_min", 60)
        commute_score = normalize_score(commute_time, 0, max_commute, invert=True)
        score = (score + commute_score) / 2

    return score


def _calculate_school_score(prop: dict) -> float:
    """Score based on nearby school ratings."""
    school_rating = prop.get("school_rating")
    if school_rating is not None:
        return normalize_score(school_rating, 0, 10)
    return 0.5


def _calculate_safety_score(prop: dict) -> float:
    """Score based on area safety."""
    crime_score = prop.get("crime_score")  # 0-100, higher = safer
    if crime_score is not None:
        return normalize_score(crime_score, 0, 100)
    return 0.5


def _calculate_amenities_score(prop: dict) -> float:
    """Score based on neighborhood amenities and walkability."""
    scores = []

    walkability = prop.get("walkability_score")
    if walkability is not None:
        scores.append(normalize_score(walkability, 0, 100))

    amenity_count = len(prop.get("amenities", []))
    scores.append(normalize_score(amenity_count, 0, 10))

    parks = prop.get("parks_nearby", 0)
    restaurants = prop.get("restaurants_nearby", 0)
    if parks or restaurants:
        scores.append(normalize_score(parks + restaurants, 0, 10))

    return sum(scores) / len(scores) if scores else 0.5


def _calculate_data_completeness(prop: dict) -> float:
    """Calculate what fraction of enrichment data is present."""
    fields = [
        "school_rating",
        "crime_score",
        "metro_distance_km",
        "commute_time_min",
        "walkability_score",
        "appreciation_rate",
    ]
    present = sum(1 for f in fields if prop.get(f) is not None)
    return present / len(fields)


def adjust_weights_from_priorities(
    current_weights: RankingWeights,
    priorities: list[str],
) -> RankingWeights:
    """
    Adjust ranking weights based on user-expressed priorities.

    This is a deterministic fallback when the LLM planner's weight
    adjustments are not available.
    """
    w = current_weights.model_dump()

    priority_text = " ".join(priorities).lower()

    if any(kw in priority_text for kw in ["safe", "security", "crime", "peaceful"]):
        w["safety"] = max(w["safety"], 0.35)

    if any(kw in priority_text for kw in ["school", "education", "child", "kid", "family"]):
        w["school"] = max(w["school"], 0.30)

    if any(kw in priority_text for kw in ["metro", "commute", "transport", "travel"]):
        w["commute"] = max(w["commute"], 0.30)

    if any(kw in priority_text for kw in ["budget", "cheap", "affordable", "value"]):
        w["budget_match"] = max(w["budget_match"], 0.40)

    if any(kw in priority_text for kw in ["restaurant", "nightlife", "park", "walkable", "amenity"]):
        w["amenities"] = max(w["amenities"], 0.30)

    # Check for negations
    if any(kw in priority_text for kw in ["don't care about school", "no school", "no kids"]):
        w["school"] = 0.0

    result = RankingWeights(**w).normalize()
    return result
