"""
HomePilot AI — Pydantic Schemas

Defines all data models for properties, user preferences, conversations,
ranking weights, tool results, and agent state. These models enforce
validation and provide serialization for the entire application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from utils.helpers import generate_id, now_iso


# ── Property Models ──────────────────────────────────────────────────────────


class PropertyImage(BaseModel):
    """A single property image."""
    url: str
    alt: str = ""


class PriceHistoryPoint(BaseModel):
    """A single data point in a property's price history."""
    date: str
    price: float


class NearbyFacility(BaseModel):
    """A nearby amenity or facility."""
    name: str
    type: str  # "school", "hospital", "metro", "park", etc.
    distance_km: float
    rating: Optional[float] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class Property(BaseModel):
    """Complete property listing data model."""
    id: str = Field(default_factory=generate_id)
    title: str
    price: float
    formatted_price: str = ""
    city: str
    locality: str
    address: str
    latitude: float
    longitude: float
    bedrooms: int
    bathrooms: int
    area_sqft: int
    property_type: str = "Apartment"  # Apartment, Villa, Independent House
    furnishing: str = "Semi-Furnished"  # Furnished, Semi-Furnished, Unfurnished
    floor: Optional[str] = None
    images: list[PropertyImage] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)

    # Enrichment data (populated by tools)
    school_rating: Optional[float] = None
    nearby_schools: list[NearbyFacility] = Field(default_factory=list)
    crime_score: Optional[float] = None  # 0-100, higher = safer
    safety_index: Optional[float] = None
    metro_distance_km: Optional[float] = None
    nearest_metro: Optional[str] = None
    commute_time_min: Optional[int] = None
    nearby_hospitals: list[NearbyFacility] = Field(default_factory=list)
    nearby_shopping: list[NearbyFacility] = Field(default_factory=list)
    walkability_score: Optional[float] = None
    parks_nearby: int = 0
    restaurants_nearby: int = 0
    supermarkets_nearby: int = 0
    price_history: list[PriceHistoryPoint] = Field(default_factory=list)
    appreciation_rate: Optional[float] = None  # annual %

    # Scoring (populated by ranking engine)
    overall_score: Optional[float] = None
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    rank: Optional[int] = None
    confidence: Optional[float] = None


class PropertySummary(BaseModel):
    """Lightweight property data for list views."""
    id: str
    title: str
    price: float
    formatted_price: str
    city: str
    locality: str
    bedrooms: int
    bathrooms: int
    area_sqft: int
    overall_score: Optional[float] = None
    rank: Optional[int] = None
    image_url: Optional[str] = None


# ── User Preferences ─────────────────────────────────────────────────────────


class UserPreferences(BaseModel):
    """Extracted user preferences from conversation."""
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    city: Optional[str] = None
    localities: list[str] = Field(default_factory=list)
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    property_type: Optional[str] = None
    furnishing: Optional[str] = None
    priorities: list[str] = Field(default_factory=list)
    must_have: list[str] = Field(default_factory=list)
    deal_breakers: list[str] = Field(default_factory=list)
    commute_destination: Optional[str] = None
    max_commute_min: Optional[int] = None

    @field_validator("bedrooms", "bathrooms", mode="before")
    @classmethod
    def coerce_to_int(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            import re
            match = re.search(r'\d+', v)
            if match:
                return int(match.group())
        return None


class RankingWeights(BaseModel):
    """Dynamic ranking weight distribution. Always sums to 1.0."""
    budget_match: float = 0.30
    commute: float = 0.20
    school: float = 0.20
    safety: float = 0.15
    amenities: float = 0.15

    def normalize(self) -> "RankingWeights":
        """Ensure weights sum to 1.0 by proportional redistribution."""
        total = (
            self.budget_match
            + self.commute
            + self.school
            + self.safety
            + self.amenities
        )
        if total == 0:
            return RankingWeights()  # Reset to defaults
        factor = 1.0 / total
        return RankingWeights(
            budget_match=round(self.budget_match * factor, 4),
            commute=round(self.commute * factor, 4),
            school=round(self.school * factor, 4),
            safety=round(self.safety * factor, 4),
            amenities=round(self.amenities * factor, 4),
        )

    def to_dict(self) -> dict[str, float]:
        return self.model_dump()


# ── Chat & Conversation ──────────────────────────────────────────────────────


class ChatMessage(BaseModel):
    """A single message in a conversation."""
    id: str = Field(default_factory=generate_id)
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = Field(default_factory=now_iso)
    properties: list[PropertySummary] = Field(default_factory=list)
    tool_calls: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """Accumulated conversation context across messages."""
    conversation_id: str = Field(default_factory=generate_id)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    weights: RankingWeights = Field(default_factory=RankingWeights)
    messages: list[ChatMessage] = Field(default_factory=list)
    favorite_ids: list[str] = Field(default_factory=list)
    last_properties: list[str] = Field(default_factory=list)  # IDs
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


# ── Tool Results ──────────────────────────────────────────────────────────────


class ToolResult(BaseModel):
    """Result from a single tool execution."""
    tool_name: str
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class PropertyScore(BaseModel):
    """Detailed score breakdown for a property."""
    property_id: str
    overall_score: float
    confidence: float
    budget_match_score: float
    commute_score: float
    school_score: float
    safety_score: float
    amenities_score: float
    weights_used: RankingWeights
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    recommendation_reason: str = ""


# ── Explanation ───────────────────────────────────────────────────────────────


class PropertyExplanation(BaseModel):
    """Explainability data for a recommended property."""
    property_id: str
    recommendation_reason: str
    pros: list[str]
    cons: list[str]
    ranking_score: float
    confidence: float
    tool_evidence: dict[str, str] = Field(default_factory=dict)
    summary: str = ""


# ── API Request/Response Models ───────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""
    message: str
    conversation_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Request body for the /search endpoint."""
    city: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    property_type: Optional[str] = None


class RankRequest(BaseModel):
    """Request body for the /rank endpoint."""
    property_ids: list[str]
    weights: Optional[RankingWeights] = None
    preferences: Optional[UserPreferences] = None
