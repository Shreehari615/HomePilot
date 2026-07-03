"""
HomePilot AI — Planner Agent

Analyzes user intent, extracts preferences, selects tools, and
adjusts ranking weights. This is the 'brain' that decides what the
agent should do for each user message.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools.llm import invoke_llm
from utils.logger import get_logger

logger = get_logger(__name__)

# Load the planner prompt template
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "planner_prompt.txt"
_PLANNER_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and extract JSON from LLM response."""
    text = text.strip()
    # Remove ```json ... ``` wrapping
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


DEFAULT_PLAN = {
    "intent": "new_search",
    "tools_needed": ["property_search"],
    "preferences": {},
    "weight_adjustments": {
        "budget_match": 0.30,
        "commute": 0.20,
        "school": 0.20,
        "safety": 0.15,
        "amenities": 0.15,
    },
    "clarification_question": None,
    "reasoning": "Default plan — could not parse LLM output.",
}


async def run_planner(
    user_message: str,
    conversation_history: str = "",
    current_preferences: str = "{}",
) -> dict[str, Any]:
    """
    Run the planner to analyze a user message and produce an execution plan.

    Args:
        user_message:          The latest message from the user.
        conversation_history:  Serialized conversation history for context.
        current_preferences:   JSON string of current accumulated preferences.

    Returns:
        A dictionary with keys: intent, tools_needed, preferences,
        weight_adjustments, clarification_question, reasoning.
    """
    prompt = _PLANNER_PROMPT_TEMPLATE.format(
        user_message=user_message,
        conversation_history=conversation_history or "No prior conversation.",
        current_preferences=current_preferences or "{}",
    )

    messages = [
        {"role": "system", "content": "You are the Planner module of HomePilot AI. Respond ONLY with valid JSON."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = await invoke_llm(messages, purpose="planner")
        cleaned = _clean_json_response(response)
        plan = json.loads(cleaned)

        # Validate required keys exist
        plan.setdefault("intent", "new_search")
        plan.setdefault("tools_needed", ["property_search"])
        plan.setdefault("preferences", {})
        plan.setdefault("weight_adjustments", DEFAULT_PLAN["weight_adjustments"])
        plan.setdefault("clarification_question", None)
        plan.setdefault("reasoning", "")

        logger.info(
            "planner_result",
            intent=plan["intent"],
            tools=plan["tools_needed"],
            reasoning=plan.get("reasoning", ""),
        )
        return plan

    except json.JSONDecodeError as e:
        logger.error("planner_json_parse_error", error=str(e))
        return {**DEFAULT_PLAN, "reasoning": f"JSON parse error: {e}"}
    except Exception as e:
        logger.error("planner_error", error=str(e))
        return {**DEFAULT_PLAN, "reasoning": f"Planner error: {e}"}


def merge_preferences(
    existing: dict[str, Any],
    new_prefs: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge new preferences into existing ones.

    New values override existing ones for the same field.
    Lists are replaced (not appended) when provided.
    None/null values in new_prefs are ignored.
    """
    merged = {**existing}
    for key, value in new_prefs.items():
        if value is not None and value != [] and value != "":
            merged[key] = value
    return merged
