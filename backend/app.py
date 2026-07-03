"""
HomePilot AI — FastAPI Application

Main application entry point. Sets up CORS, initializes database,
registers all API routes, and provides the health check endpoint.
"""

from __future__ import annotations

import traceback
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database.database import get_db
from models.schemas import ChatRequest, SearchRequest, RankRequest, RankingWeights
from models.responses import (
    BaseResponse,
    ChatResponse,
    ConversationResponse,
    HealthResponse,
    HistoryResponse,
    PropertyDetailResponse,
    RankResponse,
    SearchResponse,
)
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    setup_logging()
    logger.info("application_starting")
    # Initialize database
    db = get_db()
    logger.info("application_started", env=get_settings().app_env)
    yield
    logger.info("application_shutting_down")


# ── App Creation ─────────────────────────────────────────────────────────────


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Autonomous Property Discovery Agent for Home Buyers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ─────────────────────────────────────────────────────────────


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Application health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.app_env,
    )


# ── Chat Endpoint ────────────────────────────────────────────────────────────


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main conversational endpoint.

    Accepts a natural language message, invokes the LangGraph agent,
    and returns ranked properties with explanations.
    """
    try:
        from agents.property_agent import run_agent

        result = await run_agent(
            user_message=request.message,
            conversation_id=request.conversation_id,
        )

        # Build property models for response
        from models.schemas import Property, RankingWeights, UserPreferences
        from models.schemas import PropertyExplanation

        properties = []
        for prop_data in result.get("ranked_properties", [])[:5]:
            try:
                properties.append(Property(**prop_data))
            except Exception:
                properties.append(Property(
                    id=prop_data.get("id", ""),
                    title=prop_data.get("title", ""),
                    price=prop_data.get("price", 0),
                    formatted_price=prop_data.get("formatted_price", ""),
                    city=prop_data.get("city", ""),
                    locality=prop_data.get("locality", ""),
                    address=prop_data.get("address", ""),
                    latitude=prop_data.get("latitude", 0),
                    longitude=prop_data.get("longitude", 0),
                    bedrooms=prop_data.get("bedrooms", 0),
                    bathrooms=prop_data.get("bathrooms", 0),
                    area_sqft=prop_data.get("area_sqft", 0),
                    overall_score=prop_data.get("overall_score"),
                    score_breakdown=prop_data.get("score_breakdown", {}),
                    rank=prop_data.get("rank"),
                    confidence=prop_data.get("confidence"),
                ))

        explanations = []
        for exp_data in result.get("explanations", []):
            try:
                explanations.append(PropertyExplanation(
                    property_id=exp_data.get("property_id", ""),
                    recommendation_reason=exp_data.get("recommendation_reason", ""),
                    pros=exp_data.get("pros", []),
                    cons=exp_data.get("cons", []),
                    ranking_score=exp_data.get("confidence", 0.5),
                    confidence=exp_data.get("confidence", 0.5),
                    summary=exp_data.get("summary", ""),
                ))
            except Exception:
                pass

        weights_dict = result.get("weights", {})
        prefs_dict = result.get("preferences", {})

        return ChatResponse(
            success=True,
            reply=result.get("response_text", ""),
            conversation_id=result.get("conversation_id", ""),
            properties=properties,
            explanations=explanations,
            weights_used=RankingWeights(**weights_dict) if weights_dict else None,
            tools_called=result.get("tools_called", []),
            preferences_extracted=UserPreferences(**prefs_dict) if prefs_dict else None,
        )

    except Exception as e:
        logger.error("chat_error", error=str(e), traceback=traceback.format_exc())
        return ChatResponse(
            success=False,
            error=str(e),
            reply="I'm sorry, I encountered an error processing your request. Please try again.",
            conversation_id=request.conversation_id or "",
        )


# ── Search Endpoint ──────────────────────────────────────────────────────────


@app.post("/api/search", response_model=SearchResponse, tags=["Properties"])
async def search_properties(request: SearchRequest):
    """Direct property search with filters (non-agent)."""
    try:
        from services.property_service import search_properties as svc_search
        from models.schemas import PropertySummary
        from utils.helpers import format_inr

        results = svc_search(
            city=request.city,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            property_type=request.property_type,
        )

        summaries = [
            PropertySummary(
                id=p["id"],
                title=p["title"],
                price=p["price"],
                formatted_price=format_inr(p["price"]),
                city=p["city"],
                locality=p["locality"],
                bedrooms=p["bedrooms"],
                bathrooms=p["bathrooms"],
                area_sqft=p["area_sqft"],
                image_url=p.get("images", [{}])[0].get("url") if p.get("images") else None,
            )
            for p in results
        ]

        return SearchResponse(
            properties=summaries,
            total_count=len(summaries),
            filters_applied={
                "city": request.city,
                "budget_min": request.budget_min,
                "budget_max": request.budget_max,
                "bedrooms": request.bedrooms,
            },
        )

    except Exception as e:
        logger.error("search_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── Property Detail ──────────────────────────────────────────────────────────


@app.get("/api/property/{property_id}", response_model=PropertyDetailResponse, tags=["Properties"])
async def get_property(property_id: str):
    """Get full details for a single property."""
    from services.property_service import get_property_detail
    from models.schemas import Property
    from utils.helpers import format_inr

    prop_data = get_property_detail(property_id)
    if not prop_data:
        raise HTTPException(status_code=404, detail="Property not found")

    prop_data["formatted_price"] = format_inr(prop_data["price"])
    try:
        prop = Property(**prop_data)
    except Exception:
        prop = Property(
            id=prop_data.get("id", ""),
            title=prop_data.get("title", ""),
            price=prop_data.get("price", 0),
            formatted_price=prop_data.get("formatted_price", ""),
            city=prop_data.get("city", ""),
            locality=prop_data.get("locality", ""),
            address=prop_data.get("address", ""),
            latitude=prop_data.get("latitude", 0),
            longitude=prop_data.get("longitude", 0),
            bedrooms=prop_data.get("bedrooms", 0),
            bathrooms=prop_data.get("bathrooms", 0),
            area_sqft=prop_data.get("area_sqft", 0),
        )

    return PropertyDetailResponse(property=prop)


# ── Price History ────────────────────────────────────────────────────────────


@app.get("/api/history/{property_id}", response_model=HistoryResponse, tags=["Properties"])
async def get_history(property_id: str):
    """Get price history for a property."""
    from services.property_service import get_property_history

    history = get_property_history(property_id)
    if not history:
        raise HTTPException(status_code=404, detail="Property not found")

    return HistoryResponse(
        property_id=property_id,
        price_history=history.get("price_history", []),
        appreciation_rate=history.get("appreciation_rate"),
    )


# ── Rank Endpoint ────────────────────────────────────────────────────────────


@app.post("/api/rank", response_model=RankResponse, tags=["Ranking"])
async def rank_properties(request: RankRequest):
    """Re-rank properties with custom weights."""
    try:
        from services.property_service import get_property_detail
        from services.ranking_service import compute_property_scores
        from agents.ranking_agent import generate_explanations
        from models.schemas import Property, PropertyExplanation

        properties = []
        for pid in request.property_ids:
            prop = get_property_detail(pid)
            if prop:
                properties.append(prop)

        if not properties:
            raise HTTPException(status_code=404, detail="No valid properties found")

        weights = request.weights or RankingWeights()
        prefs = request.preferences.model_dump() if request.preferences else {}

        ranked = compute_property_scores(properties, weights, prefs)
        explanations_data = await generate_explanations(ranked, prefs, weights.model_dump())

        ranked_models = []
        for prop_data in ranked:
            try:
                ranked_models.append(Property(**prop_data))
            except Exception:
                pass

        explanation_models = []
        for exp in explanations_data:
            try:
                explanation_models.append(PropertyExplanation(
                    property_id=exp.get("property_id", ""),
                    recommendation_reason=exp.get("recommendation_reason", ""),
                    pros=exp.get("pros", []),
                    cons=exp.get("cons", []),
                    ranking_score=exp.get("confidence", 0.5),
                    confidence=exp.get("confidence", 0.5),
                ))
            except Exception:
                pass

        return RankResponse(
            ranked_properties=ranked_models,
            explanations=explanation_models,
            weights_used=weights,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("rank_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── Conversation History ─────────────────────────────────────────────────────


@app.get("/api/conversation", response_model=ConversationResponse, tags=["Conversation"])
async def get_conversation(conversation_id: str = ""):
    """Retrieve conversation history and preferences."""
    if not conversation_id:
        # List all conversations
        from services.conversation_service import list_conversations
        conversations = list_conversations()
        return ConversationResponse(
            message="Use conversation_id parameter to get specific conversation",
            messages=[],
        )

    from services.conversation_service import get_conversation_messages
    from models.schemas import ChatMessage, UserPreferences

    data = get_conversation_messages(conversation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [ChatMessage(**m) for m in data.get("messages", [])]
    prefs = UserPreferences(**data.get("preferences", {}))

    return ConversationResponse(
        conversation_id=conversation_id,
        messages=messages,
        preferences=prefs,
    )


# ── Browse All Properties ────────────────────────────────────────────────────


@app.get("/api/properties", tags=["Properties"])
async def list_all_properties():
    """Browse all available properties."""
    from services.property_service import browse_all_properties
    from models.schemas import PropertySummary
    from utils.helpers import format_inr

    all_props = browse_all_properties()
    summaries = [
        {
            "id": p["id"],
            "title": p["title"],
            "price": p["price"],
            "formatted_price": format_inr(p["price"]),
            "city": p["city"],
            "locality": p["locality"],
            "bedrooms": p["bedrooms"],
            "bathrooms": p["bathrooms"],
            "area_sqft": p["area_sqft"],
            "image_url": p.get("images", [{}])[0].get("url") if p.get("images") else None,
        }
        for p in all_props
    ]
    return {"properties": summaries, "total_count": len(summaries)}


# ── Run ──────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )

