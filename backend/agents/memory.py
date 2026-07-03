"""
HomePilot AI — Conversation Memory

Manages conversation context persistence using LangGraph's MemorySaver,
SQLite for structured preferences, and ChromaDB for semantic search.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from langgraph.checkpoint.memory import MemorySaver

from database.database import get_db
from models.schemas import ConversationContext, UserPreferences, RankingWeights, ChatMessage
from utils.logger import get_logger
from utils.helpers import generate_id, now_iso

logger = get_logger(__name__)

# Shared checkpointer for LangGraph
_checkpointer = MemorySaver()


def get_checkpointer() -> MemorySaver:
    """Get the shared LangGraph checkpointer."""
    return _checkpointer


class ConversationMemory:
    """
    Manages conversation state across multiple turns.

    Combines:
    - In-memory context for the current session
    - SQLite persistence for cross-session recovery
    - ChromaDB for semantic search over past conversations
    """

    def __init__(self, conversation_id: str | None = None):
        self.db = get_db()
        self.conversation_id = conversation_id or generate_id()
        self._context: ConversationContext | None = None

    @property
    def context(self) -> ConversationContext:
        """Get or load the conversation context."""
        if self._context is None:
            self._context = self._load_or_create()
        return self._context

    def _load_or_create(self) -> ConversationContext:
        """Load existing conversation or create a new one."""
        data = self.db.load_conversation(self.conversation_id)
        if data:
            logger.info("conversation_loaded", id=self.conversation_id)
            return ConversationContext(
                conversation_id=self.conversation_id,
                preferences=UserPreferences(**data.get("preferences", {})),
                weights=RankingWeights(**data.get("weights", {})),
                messages=[ChatMessage(**m) for m in data.get("messages", [])],
                favorite_ids=data.get("favorite_ids", []),
                created_at=data.get("created_at", now_iso()),
                updated_at=data.get("updated_at", now_iso()),
            )
        logger.info("conversation_created", id=self.conversation_id)
        return ConversationContext(conversation_id=self.conversation_id)

    def add_message(self, role: str, content: str, **kwargs: Any) -> ChatMessage:
        """Add a message to the conversation history."""
        msg = ChatMessage(role=role, content=content, **kwargs)
        self.context.messages.append(msg)
        self.context.updated_at = now_iso()
        return msg

    def update_preferences(self, new_prefs: dict[str, Any]) -> UserPreferences:
        """Merge new preferences into existing ones."""
        current = self.context.preferences.model_dump()
        for key, value in new_prefs.items():
            if value is not None and value != [] and value != "":
                current[key] = value
        self.context.preferences = UserPreferences(**current)
        return self.context.preferences

    def update_weights(self, new_weights: dict[str, float]) -> RankingWeights:
        """Update ranking weights and normalize to sum to 1.0."""
        self.context.weights = RankingWeights(**new_weights).normalize()
        return self.context.weights

    def set_last_properties(self, property_ids: list[str]) -> None:
        """Track the last set of properties shown to the user."""
        self.context.last_properties = property_ids

    def toggle_favorite(self, property_id: str) -> bool:
        """Toggle a property as favorite. Returns True if added, False if removed."""
        if property_id in self.context.favorite_ids:
            self.context.favorite_ids.remove(property_id)
            return False
        self.context.favorite_ids.append(property_id)
        return True

    def get_history_text(self, last_n: int = 10) -> str:
        """Get conversation history as formatted text for LLM context."""
        messages = self.context.messages[-last_n:]
        lines = []
        for msg in messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)

    def get_preferences_json(self) -> str:
        """Get current preferences as a JSON string."""
        return self.context.preferences.model_dump_json()

    def save(self) -> None:
        """Persist the conversation to SQLite and ChromaDB."""
        ctx = self.context
        self.db.save_conversation(
            conversation_id=ctx.conversation_id,
            preferences=ctx.preferences.model_dump(),
            weights=ctx.weights.model_dump(),
            messages=[m.model_dump() for m in ctx.messages],
            favorite_ids=ctx.favorite_ids,
            created_at=ctx.created_at,
            updated_at=ctx.updated_at,
        )

        # Store latest exchange in semantic memory
        if len(ctx.messages) >= 2:
            last_user = ctx.messages[-2] if ctx.messages[-2].role == "user" else None
            last_assistant = ctx.messages[-1] if ctx.messages[-1].role == "assistant" else None
            if last_user and last_assistant:
                memory_text = (
                    f"User asked: {last_user.content}\n"
                    f"Preferences: {ctx.preferences.model_dump_json()}\n"
                    f"Response summary: {last_assistant.content[:300]}"
                )
                self.db.store_memory(
                    conversation_id=ctx.conversation_id,
                    text=memory_text,
                    metadata={
                        "type": "conversation_turn",
                        "city": ctx.preferences.city or "",
                    },
                )

        logger.info("conversation_saved", id=ctx.conversation_id)

    def search_relevant_context(self, query: str, n_results: int = 3) -> list[dict]:
        """Search semantic memory for context relevant to the query."""
        return self.db.search_memory(
            query=query,
            n_results=n_results,
            conversation_id=self.conversation_id,
        )
