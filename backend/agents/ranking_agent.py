"""
HomePilot AI — Ranking Agent

LLM-assisted ranking weight adjustment and explanation generation.
Works alongside the deterministic ranking_service to produce
human-readable explanations.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools.llm import invoke_llm
from utils.logger import get_logger
from utils.helpers import format_inr

logger = get_logger(__name__)

_RANKING_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "ranking_prompt.txt"
)
_RANKING_PROMPT_TEMPLATE = _RANKING_PROMPT_PATH.read_text(encoding="utf-8")


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and extract JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


async def generate_explanations(
    ranked_properties: list[dict[str, Any]],
    user_preferences: dict[str, Any],
    weights_used: dict[str, float],
) -> list[dict[str, Any]]:
    """
    Generate natural-language explanations for ranked properties.

    Uses the LLM to produce recommendation reasons, pros, cons,
    and confidence assessments for each ranked property.

    Args:
        ranked_properties: Properties sorted by score, each with score_breakdown.
        user_preferences:  The user's accumulated preferences.
        weights_used:      The ranking weights that were applied.

    Returns:
        List of explanation dicts with property_id, recommendation_reason,
        pros, cons, confidence, summary.
    """
    # Build compact property summaries for the LLM
    prop_summaries = []
    for prop in ranked_properties[:5]:  # Top 5 only to save tokens
        prop_summaries.append({
            "id": prop.get("id", ""),
            "title": prop.get("title", ""),
            "price": format_inr(prop.get("price", 0)),
            "locality": prop.get("locality", ""),
            "city": prop.get("city", ""),
            "bedrooms": prop.get("bedrooms", 0),
            "area_sqft": prop.get("area_sqft", 0),
            "overall_score": prop.get("overall_score", 0),
            "score_breakdown": prop.get("score_breakdown", {}),
            "metro_distance_km": prop.get("metro_distance_km"),
            "school_rating": prop.get("school_rating"),
            "crime_score": prop.get("crime_score"),
            "walkability_score": prop.get("walkability_score"),
            "appreciation_rate": prop.get("appreciation_rate"),
            "amenities": prop.get("amenities", [])[:5],
        })

    prompt = _RANKING_PROMPT_TEMPLATE.format(
        properties_data=json.dumps(prop_summaries, indent=2),
        user_preferences=json.dumps(user_preferences, indent=2),
        weights_used=json.dumps(weights_used, indent=2),
    )

    messages = [
        {
            "role": "system",
            "content": "You are the Ranking Explanation module. Respond ONLY with a valid JSON array.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = await invoke_llm(messages, purpose="ranking_explanation")
        cleaned = _clean_json_response(response)
        explanations = json.loads(cleaned)

        if not isinstance(explanations, list):
            explanations = [explanations]

        logger.info(
            "explanations_generated",
            count=len(explanations),
        )
        return explanations

    except Exception as e:
        logger.error("explanation_generation_failed", error=str(e))
        # Fallback: generate basic explanations from score data
        return _generate_fallback_explanations(ranked_properties)


def _generate_fallback_explanations(
    properties: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate basic explanations when LLM call fails."""
    explanations = []
    for prop in properties[:5]:
        pros = []
        cons = []
        breakdown = prop.get("score_breakdown", {})

        if breakdown.get("budget_match", 0) > 0.7:
            pros.append(f"✓ Good budget match at {format_inr(prop.get('price', 0))}")
        elif breakdown.get("budget_match", 0) < 0.4:
            cons.append(f"✗ Stretches budget at {format_inr(prop.get('price', 0))}")

        if prop.get("metro_distance_km") and prop["metro_distance_km"] < 1.5:
            pros.append(f"✓ Close to metro ({prop['metro_distance_km']}km)")
        elif prop.get("metro_distance_km") and prop["metro_distance_km"] > 3.0:
            cons.append(f"✗ Far from metro ({prop['metro_distance_km']}km)")

        if prop.get("school_rating") and prop["school_rating"] > 8.0:
            pros.append(f"✓ Excellent schools nearby (rating {prop['school_rating']}/10)")
        elif prop.get("school_rating") and prop["school_rating"] < 6.0:
            cons.append(f"✗ Below average schools (rating {prop['school_rating']}/10)")

        if prop.get("crime_score") and prop["crime_score"] > 75:
            pros.append(f"✓ Very safe area (safety score {prop['crime_score']}/100)")
        elif prop.get("crime_score") and prop["crime_score"] < 60:
            cons.append(f"✗ Safety concerns (score {prop['crime_score']}/100)")

        if prop.get("walkability_score") and prop["walkability_score"] > 75:
            pros.append(f"✓ Highly walkable ({prop['walkability_score']}/100)")

        score = prop.get("overall_score", 0)
        explanations.append({
            "property_id": prop.get("id", ""),
            "recommendation_reason": f"Scored {score:.1f}/100 based on your preferences.",
            "pros": pros or ["✓ Meets basic criteria"],
            "cons": cons or ["✗ No significant drawbacks found"],
            "confidence": min(0.95, score / 100 + 0.1),
            "summary": f"{prop.get('title', 'Property')} in {prop.get('locality', '')} — "
                       f"overall score {score:.1f}/100.",
        })

    return explanations
