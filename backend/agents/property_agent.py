"""
HomePilot AI — Property Agent (LangGraph Core)

The central LangGraph StateGraph that orchestrates the autonomous
property discovery workflow. Nodes dynamically decide which tools
to call, enrich properties, rank them, and generate explanations.

Graph Flow:
    START → planner → tool_router → [property_search] → [enrichment] → ranking → explanation → memory_update → END

The planner decides which tools to invoke. The tool_router fans out
to only the required tools. This is NOT a fixed pipeline.
"""

from __future__ import annotations

import json
import operator
import time
from pathlib import Path
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agents.memory import ConversationMemory, get_checkpointer
from agents.planner import merge_preferences, run_planner
from agents.ranking_agent import generate_explanations
from services.ranking_service import compute_property_scores
from models.schemas import RankingWeights
from tools.llm import invoke_llm
from tools.property_search import property_search
from tools.google_maps import google_maps_tool
from tools.school_tool import school_tool
from tools.crime_tool import crime_tool
from tools.price_history import price_history_tool
from tools.neighborhood import neighborhood_tool
from utils.logger import get_logger
from utils.helpers import format_inr

logger = get_logger(__name__)

# Load system prompt
_SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"
_SYSTEM_PROMPT = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


# ── Agent State ──────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    """State flowing through the LangGraph workflow."""
    # Input
    user_message: str
    conversation_id: str

    # Planner output
    plan: dict[str, Any]
    intent: str
    tools_needed: list[str]

    # Accumulated context
    preferences: dict[str, Any]
    weights: dict[str, float]

    # Tool results
    raw_properties: list[dict[str, Any]]
    enrichment_data: dict[str, dict[str, Any]]

    # Output
    ranked_properties: list[dict[str, Any]]
    explanations: list[dict[str, Any]]
    response_text: str
    tools_called: list[str]


# ── Node Functions ───────────────────────────────────────────────────────────


async def planner_node(state: AgentState) -> dict:
    """
    Analyze user intent and decide execution strategy.

    This node:
    1. Loads conversation memory
    2. Runs the LLM planner
    3. Extracts preferences and tool selection
    4. Adjusts ranking weights
    """
    memory = state.get("memory")
    if not memory:
        memory = ConversationMemory(state.get("conversation_id"))

    # Add user message to memory
    memory.add_message("user", state["user_message"])

    # Run planner with conversation context
    plan = await run_planner(
        user_message=state["user_message"],
        conversation_history=memory.get_history_text(),
        current_preferences=memory.get_preferences_json(),
    )

    # Merge preferences
    new_prefs = plan.get("preferences", {})
    merged_prefs = merge_preferences(
        memory.context.preferences.model_dump(),
        new_prefs,
    )
    memory.update_preferences(new_prefs)

    # Update weights
    weight_adj = plan.get("weight_adjustments", {})
    if weight_adj:
        memory.update_weights(weight_adj)
        
    memory.save()

    return {
        "plan": plan,
        "intent": plan.get("intent", "new_search"),
        "tools_needed": plan.get("tools_needed", []),
        "preferences": merged_prefs,
        "weights": memory.context.weights.model_dump(),
        "tools_called": [],
    }


async def property_search_node(state: AgentState) -> dict:
    """Search for properties matching user preferences."""
    prefs = state.get("preferences", {})

    result = property_search.invoke({
        "budget_min": prefs.get("budget_min"),
        "budget_max": prefs.get("budget_max"),
        "city": prefs.get("city"),
        "bedrooms": prefs.get("bedrooms"),
        "bathrooms": prefs.get("bathrooms"),
        "property_type": prefs.get("property_type"),
    })

    properties = result.get("properties", [])
    tools_called = state.get("tools_called", []) + ["property_search"]

    logger.info("property_search_complete", count=len(properties))

    return {
        "raw_properties": properties,
        "tools_called": tools_called,
    }


async def enrichment_node(state: AgentState) -> dict:
    """
    Enrich properties with data from selected tools.

    Only calls tools that the planner selected. Processes each
    property independently.
    """
    properties = state.get("raw_properties", [])
    tools_needed = state.get("tools_needed", [])
    tools_called = state.get("tools_called", [])

    if not properties:
        return {"raw_properties": properties, "tools_called": tools_called}

    enriched = []
    for prop in properties:
        locality = prop.get("locality", "")
        city = prop.get("city", "")
        enriched_prop = {**prop}

        # Google Maps
        if "google_maps" in tools_needed:
            try:
                maps_data = google_maps_tool.invoke({"locality": locality, "city": city})
                enriched_prop["metro_distance_km"] = maps_data.get("metro_distance_km")
                enriched_prop["nearest_metro"] = maps_data.get("nearest_metro")
                enriched_prop["commute_time_min"] = maps_data.get("commute_time_min")
                enriched_prop["nearby_hospitals"] = maps_data.get("nearby_hospitals", [])
                enriched_prop["nearby_shopping"] = maps_data.get("nearby_shopping", [])
                if "google_maps" not in tools_called:
                    tools_called.append("google_maps")
            except Exception as e:
                logger.error("maps_enrichment_failed", property_id=prop["id"], error=str(e))

        # Schools
        if "school_tool" in tools_needed:
            try:
                school_data = school_tool.invoke({"locality": locality, "city": city})
                enriched_prop["school_rating"] = school_data.get("average_rating")
                enriched_prop["nearby_schools"] = school_data.get("nearby_schools", [])
                if "school_tool" not in tools_called:
                    tools_called.append("school_tool")
            except Exception as e:
                logger.error("school_enrichment_failed", property_id=prop["id"], error=str(e))

        # Crime / Safety
        if "crime_tool" in tools_needed:
            try:
                crime_data = crime_tool.invoke({"locality": locality, "city": city})
                enriched_prop["crime_score"] = crime_data.get("safety_score")
                enriched_prop["safety_index"] = crime_data.get("crime_index")
                if "crime_tool" not in tools_called:
                    tools_called.append("crime_tool")
            except Exception as e:
                logger.error("crime_enrichment_failed", property_id=prop["id"], error=str(e))

        # Price History
        if "price_history" in tools_needed:
            try:
                history_data = price_history_tool.invoke({
                    "property_id": prop["id"],
                    "current_price": prop.get("price", 0),
                    "locality": locality,
                })
                enriched_prop["appreciation_rate"] = history_data.get("appreciation_rate_annual")
                enriched_prop["price_history"] = history_data.get("price_history", [])
                if "price_history" not in tools_called:
                    tools_called.append("price_history")
            except Exception as e:
                logger.error("history_enrichment_failed", property_id=prop["id"], error=str(e))

        # Neighborhood
        if "neighborhood" in tools_needed:
            try:
                hood_data = neighborhood_tool.invoke({"locality": locality, "city": city})
                enriched_prop["walkability_score"] = hood_data.get("walkability_score")
                enriched_prop["parks_nearby"] = hood_data.get("parks_count", 0)
                enriched_prop["restaurants_nearby"] = hood_data.get("restaurants_count", 0)
                enriched_prop["supermarkets_nearby"] = hood_data.get("supermarkets_count", 0)
                if "neighborhood" not in tools_called:
                    tools_called.append("neighborhood")
            except Exception as e:
                logger.error("neighborhood_enrichment_failed", property_id=prop["id"], error=str(e))

        enriched.append(enriched_prop)

    return {
        "raw_properties": enriched,
        "tools_called": tools_called,
    }


async def ranking_node(state: AgentState) -> dict:
    """Rank enriched properties using the weighted scoring algorithm."""
    properties = state.get("raw_properties", [])
    weights = RankingWeights(**state.get("weights", {}))
    preferences = state.get("preferences", {})

    if not properties:
        return {"ranked_properties": []}

    ranked = compute_property_scores(properties, weights, preferences)
    return {"ranked_properties": ranked}


async def explanation_node(state: AgentState) -> dict:
    """Generate natural-language explanations for recommendations."""
    ranked = state.get("ranked_properties", [])
    preferences = state.get("preferences", {})
    weights = state.get("weights", {})

    if not ranked:
        return {"explanations": []}

    explanations = await generate_explanations(ranked, preferences, weights)
    return {"explanations": explanations}


async def response_node(state: AgentState) -> dict:
    """
    Generate the final response using the LLM.

    Combines ranked properties, explanations, and conversation context
    into a natural, conversational response.
    """
    plan = state.get("plan", {})
    intent = state.get("intent", "")
    ranked = state.get("ranked_properties", [])
    explanations = state.get("explanations", [])
    preferences = state.get("preferences", {})
    tools_called = state.get("tools_called", [])
    memory = state.get("memory")

    # For clarification, just pass through
    clarification = plan.get("clarification_question")
    if intent == "clarification_needed" and clarification:
        return {"response_text": clarification}

    # Build context for the response LLM
    context_parts = []

    if ranked:
        top_props = []
        for i, prop in enumerate(ranked[:5]):
            exp = next(
                (e for e in explanations if e.get("property_id") == prop.get("id")),
                {},
            )
            top_props.append({
                "rank": i + 1,
                "title": prop.get("title", ""),
                "price": format_inr(prop.get("price", 0)),
                "locality": prop.get("locality", ""),
                "city": prop.get("city", ""),
                "bedrooms": prop.get("bedrooms", 0),
                "bathrooms": prop.get("bathrooms", 0),
                "area_sqft": prop.get("area_sqft", 0),
                "score": prop.get("overall_score", 0),
                "pros": exp.get("pros", []),
                "cons": exp.get("cons", []),
                "reason": exp.get("recommendation_reason", ""),
            })
        context_parts.append(f"Ranked Properties:\n{json.dumps(top_props, indent=2)}")

    context_parts.append(f"Tools Used: {', '.join(tools_called) if tools_called else 'None'}")
    context_parts.append(f"User Preferences: {json.dumps(preferences, indent=2)}")
    context_parts.append(f"Intent: {intent}")

    conversation_history = ""
    memory = ConversationMemory(state.get("conversation_id"))
    if memory:
        conversation_history = memory.get_history_text(last_n=6)

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Based on the following data, generate a helpful conversational response "
            f"for the user. Be specific, reference actual property data, and explain "
            f"your recommendations.\n\n"
            f"Conversation History:\n{conversation_history}\n\n"
            f"Current User Message: {state.get('user_message', '')}\n\n"
            + "\n".join(context_parts)
        )},
    ]

    response_text = await invoke_llm(messages, purpose="response_generation")
    return {"response_text": response_text}


async def memory_update_node(state: AgentState) -> dict:
    """Persist conversation state to memory and database."""
    memory = ConversationMemory(state.get("conversation_id"))
    if not memory:
        return {}

    # Add assistant response
    ranked = state.get("ranked_properties", [])
    property_ids = [p.get("id", "") for p in ranked[:5]]

    memory.add_message(
        "assistant",
        state.get("response_text", ""),
        properties=[],
        tool_calls=state.get("tools_called", []),
    )
    memory.set_last_properties(property_ids)
    memory.save()

    return {}


# ── Routing Logic ────────────────────────────────────────────────────────────


def should_search(state: AgentState) -> str:
    """Determine if property search is needed."""
    intent = state.get("intent", "")
    tools = state.get("tools_needed", [])

    if intent == "clarification_needed":
        return "respond"
    if intent == "general_question":
        return "respond"
    if "property_search" in tools:
        return "search"
    if tools:
        return "enrich_only"
    return "respond"


def should_enrich(state: AgentState) -> str:
    """Determine if enrichment tools are needed."""
    tools = state.get("tools_needed", [])
    enrichment_tools = {"google_maps", "school_tool", "crime_tool", "price_history", "neighborhood"}
    if enrichment_tools.intersection(set(tools)):
        return "enrich"
    return "rank"


# ── Graph Construction ───────────────────────────────────────────────────────


def build_agent_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for the property agent.

    The graph structure dynamically routes based on planner decisions:

        START
          ↓
        planner ──→ should_search?
          │              │
          │    ┌─────────┼──────────────┐
          │    ↓         ↓              ↓
          │  search → enrich? → rank → explain → respond → memory → END
          │              │
          │         enrich_only → rank → explain → respond → memory → END
          │              │
          └──────→ respond directly → memory → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("property_search", property_search_node)
    workflow.add_node("enrichment", enrichment_node)
    workflow.add_node("ranking", ranking_node)
    workflow.add_node("explanation", explanation_node)
    workflow.add_node("response", response_node)
    workflow.add_node("memory_update", memory_update_node)

    # Set entry point
    workflow.set_entry_point("planner")

    # Conditional routing after planner
    workflow.add_conditional_edges(
        "planner",
        should_search,
        {
            "search": "property_search",
            "enrich_only": "enrichment",
            "respond": "response",
        },
    )

    # After property search, check if enrichment is needed
    workflow.add_conditional_edges(
        "property_search",
        should_enrich,
        {
            "enrich": "enrichment",
            "rank": "ranking",
        },
    )

    # Linear flow: enrichment → ranking → explanation → response → memory
    workflow.add_edge("enrichment", "ranking")
    workflow.add_edge("ranking", "explanation")
    workflow.add_edge("explanation", "response")
    workflow.add_edge("response", "memory_update")
    workflow.add_edge("memory_update", END)

    return workflow


# ── Compiled Graph ───────────────────────────────────────────────────────────

_compiled_graph = None


def get_agent():
    """Get or create the compiled agent graph."""
    global _compiled_graph
    if _compiled_graph is None:
        workflow = build_agent_graph()
        _compiled_graph = workflow.compile(checkpointer=get_checkpointer())
        logger.info("agent_graph_compiled")
    return _compiled_graph


async def run_agent(
    user_message: str,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the full agent pipeline for a user message.

    Args:
        user_message:     The user's natural language input.
        conversation_id:  Optional conversation ID for context continuity.

    Returns:
        Dictionary with response_text, ranked_properties, explanations,
        conversation_id, tools_called, and preferences.
    """
    from services.conversation_service import get_or_create_conversation

    memory = get_or_create_conversation(conversation_id)
    agent = get_agent()

    initial_state: AgentState = {
        "user_message": user_message,
        "conversation_id": memory.conversation_id,
        "plan": {},
        "intent": "",
        "tools_needed": [],
        "preferences": memory.context.preferences.model_dump(),
        "weights": memory.context.weights.model_dump(),
        "raw_properties": [],
        "enrichment_data": {},
        "ranked_properties": [],
        "explanations": [],
        "response_text": "",
        "tools_called": [],
    }

    config = {"configurable": {"thread_id": memory.conversation_id}}

    start = time.perf_counter()
    result = await agent.ainvoke(initial_state, config=config)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info(
        "agent_run_complete",
        conversation_id=memory.conversation_id,
        duration_ms=round(elapsed, 2),
        tools_called=result.get("tools_called", []),
        properties_found=len(result.get("ranked_properties", [])),
    )

    return {
        "response_text": result.get("response_text", ""),
        "ranked_properties": result.get("ranked_properties", []),
        "explanations": result.get("explanations", []),
        "conversation_id": memory.conversation_id,
        "tools_called": result.get("tools_called", []),
        "preferences": result.get("preferences", {}),
        "weights": result.get("weights", {}),
    }
