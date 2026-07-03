"""
HomePilot AI — Conversation Service

Manages conversation lifecycle: creation, retrieval, history listing.
Bridges the API layer with the memory and database layers.
"""

from __future__ import annotations

from typing import Any, Optional

from agents.memory import ConversationMemory
from database.database import get_db
from utils.logger import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)

# In-memory cache of active conversations
_active_conversations: dict[str, ConversationMemory] = {}


def get_or_create_conversation(
    conversation_id: str | None = None,
) -> ConversationMemory:
    """
    Get an existing conversation or create a new one.

    Maintains an in-memory cache of active conversations for fast access.
    """
    if conversation_id and conversation_id in _active_conversations:
        return _active_conversations[conversation_id]

    memory = ConversationMemory(conversation_id=conversation_id)
    _active_conversations[memory.conversation_id] = memory
    return memory


def list_conversations() -> list[dict[str, Any]]:
    """List all saved conversations with summary info."""
    db = get_db()
    return db.list_conversations()


def get_conversation_messages(
    conversation_id: str,
) -> dict[str, Any] | None:
    """Get full conversation messages and preferences."""
    db = get_db()
    data = db.load_conversation(conversation_id)
    if not data:
        return None
    return data
