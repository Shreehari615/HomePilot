"""
HomePilot AI — Application Configuration

Loads settings from environment variables with sensible defaults.
Uses Pydantic Settings for type-safe configuration management.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the HomePilot AI backend."""

    # ── Application ──────────────────────────────────────────────────────
    app_name: str = Field(default="HomePilot AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    # ── LLM Provider ─────────────────────────────────────────────────────
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")

    # ── OpenAI ───────────────────────────────────────────────────────────
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: Optional[str] = Field(default=None, alias="OPENAI_BASE_URL")

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite+aiosqlite:///./homepilot.db",
        alias="DATABASE_URL",
    )
    chroma_persist_dir: str = Field(
        default="./chroma_data",
        alias="CHROMA_PERSIST_DIR",
    )

    # ── Server ───────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # ── CORS ─────────────────────────────────────────────────────────────
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ── Default Ranking Weights (sum to 1.0) ─────────────────────────────
    weight_budget: float = 0.30
    weight_commute: float = 0.20
    weight_school: float = 0.20
    weight_safety: float = 0.15
    weight_amenities: float = 0.15

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def default_weights(self) -> dict[str, float]:
        """Return default ranking weights as a dictionary."""
        return {
            "budget_match": self.weight_budget,
            "commute": self.weight_commute,
            "school": self.weight_school,
            "safety": self.weight_safety,
            "amenities": self.weight_amenities,
        }

    @property
    def base_dir(self) -> Path:
        """Return the project base directory."""
        return Path(__file__).resolve().parent

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
