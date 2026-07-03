"""
HomePilot AI — API Response Models

Standardized response wrappers for all API endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from models.schemas import (
    ChatMessage,
    Property,
    PropertyExplanation,
    PropertySummary,
    RankingWeights,
    UserPreferences,
)


class BaseResponse(BaseModel):
    """Base response wrapper with success/error fields."""
    success: bool = True
    message: str = "OK"
    error: Optional[str] = None


class ChatResponse(BaseResponse):
    """Response from the /chat endpoint."""
    reply: str = ""
    conversation_id: str = ""
    properties: list[Property] = Field(default_factory=list)
    explanations: list[PropertyExplanation] = Field(default_factory=list)
    weights_used: Optional[RankingWeights] = None
    tools_called: list[str] = Field(default_factory=list)
    preferences_extracted: Optional[UserPreferences] = None


class SearchResponse(BaseResponse):
    """Response from the /search endpoint."""
    properties: list[PropertySummary] = Field(default_factory=list)
    total_count: int = 0
    filters_applied: dict[str, Any] = Field(default_factory=dict)


class PropertyDetailResponse(BaseResponse):
    """Response from the /property/{id} endpoint."""
    property: Optional[Property] = None


class HistoryResponse(BaseResponse):
    """Response from the /history/{id} endpoint."""
    property_id: str = ""
    price_history: list[dict[str, Any]] = Field(default_factory=list)
    appreciation_rate: Optional[float] = None


class RankResponse(BaseResponse):
    """Response from the /rank endpoint."""
    ranked_properties: list[Property] = Field(default_factory=list)
    explanations: list[PropertyExplanation] = Field(default_factory=list)
    weights_used: RankingWeights = Field(default_factory=RankingWeights)


class ConversationResponse(BaseResponse):
    """Response from the /conversation endpoint."""
    conversation_id: str = ""
    messages: list[ChatMessage] = Field(default_factory=list)
    preferences: Optional[UserPreferences] = None


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str = "healthy"
    app_name: str = ""
    environment: str = ""
    version: str = "1.0.0"
