"""
HomePilot AI — Database Layer

Manages SQLite (via SQLAlchemy async) for structured data storage
and ChromaDB for semantic vector search over conversation memory.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

import chromadb

from config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
Base = declarative_base()


# ── SQLAlchemy ORM Models ────────────────────────────────────────────────────


class ConversationRecord(Base):
    """Stores conversation metadata and accumulated context."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    preferences_json = Column(Text, default="{}")
    weights_json = Column(Text, default="{}")
    messages_json = Column(Text, default="[]")
    favorite_ids_json = Column(Text, default="[]")
    created_at = Column(String, default="")
    updated_at = Column(String, default="")


class PropertyRecord(Base):
    """Stores property data for quick retrieval."""
    __tablename__ = "properties"

    id = Column(String, primary_key=True)
    data_json = Column(Text, default="{}")
    city = Column(String, index=True)
    price = Column(Float, index=True)
    bedrooms = Column(Integer, index=True)


class FavoriteRecord(Base):
    """Tracks favorited properties per conversation."""
    __tablename__ = "favorites"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, index=True)
    property_id = Column(String)
    created_at = Column(String, default="")


# ── Database Manager ─────────────────────────────────────────────────────────


class DatabaseManager:
    """
    Manages both SQLite and ChromaDB connections.

    Provides methods for conversation CRUD, property storage,
    and semantic memory search.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._engine = None
        self._session_factory = None
        self._chroma_client = None

    def initialize(self) -> None:
        """Initialize database connections and create tables."""
        # SQLite setup — using sync engine for simplicity with SQLite
        db_path = self.settings.database_url.replace(
            "sqlite+aiosqlite:///", "sqlite:///"
        )
        self._engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

        # ChromaDB setup
        self._chroma_client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir
        )
        logger.info(
            "database_initialized",
            sqlite=db_path,
            chroma=self.settings.chroma_persist_dir,
        )

    def get_session(self) -> Session:
        """Get a new SQLAlchemy session."""
        if not self._session_factory:
            self.initialize()
        return self._session_factory()

    @property
    def chroma(self) -> chromadb.PersistentClient:
        """Get the ChromaDB client."""
        if not self._chroma_client:
            self.initialize()
        return self._chroma_client

    def get_memory_collection(self) -> chromadb.Collection:
        """Get or create the conversation memory collection."""
        return self.chroma.get_or_create_collection(
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"},
        )

    # ── Conversation CRUD ────────────────────────────────────────────────

    def save_conversation(
        self,
        conversation_id: str,
        preferences: dict,
        weights: dict,
        messages: list[dict],
        favorite_ids: list[str],
        created_at: str = "",
        updated_at: str = "",
    ) -> None:
        """Save or update a conversation record."""
        with self.get_session() as session:
            record = session.get(ConversationRecord, conversation_id)
            if record:
                record.preferences_json = json.dumps(preferences)
                record.weights_json = json.dumps(weights)
                record.messages_json = json.dumps(messages)
                record.favorite_ids_json = json.dumps(favorite_ids)
                record.updated_at = updated_at
            else:
                record = ConversationRecord(
                    id=conversation_id,
                    preferences_json=json.dumps(preferences),
                    weights_json=json.dumps(weights),
                    messages_json=json.dumps(messages),
                    favorite_ids_json=json.dumps(favorite_ids),
                    created_at=created_at,
                    updated_at=updated_at,
                )
                session.add(record)
            session.commit()

    def load_conversation(self, conversation_id: str) -> Optional[dict]:
        """Load a conversation record by ID."""
        with self.get_session() as session:
            record = session.get(ConversationRecord, conversation_id)
            if not record:
                return None
            return {
                "id": record.id,
                "preferences": json.loads(record.preferences_json),
                "weights": json.loads(record.weights_json),
                "messages": json.loads(record.messages_json),
                "favorite_ids": json.loads(record.favorite_ids_json),
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }

    def list_conversations(self) -> list[dict]:
        """List all conversations with summary info."""
        with self.get_session() as session:
            records = session.query(ConversationRecord).all()
            return [
                {
                    "id": r.id,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                    "message_count": len(json.loads(r.messages_json)),
                }
                for r in records
            ]

    # ── Semantic Memory ──────────────────────────────────────────────────

    def store_memory(
        self,
        conversation_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store a text in the semantic memory collection."""
        collection = self.get_memory_collection()
        doc_id = f"{conversation_id}_{len(collection.get()['ids'])}"
        meta = {"conversation_id": conversation_id}
        if metadata:
            meta.update(metadata)
        collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[doc_id],
        )

    def search_memory(
        self,
        query: str,
        n_results: int = 5,
        conversation_id: str | None = None,
    ) -> list[dict]:
        """Search semantic memory for relevant past context."""
        collection = self.get_memory_collection()
        where_filter = None
        if conversation_id:
            where_filter = {"conversation_id": conversation_id}
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )
            return [
                {
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        except Exception as e:
            logger.warning("memory_search_failed", error=str(e))
            return []

    # ── Property Storage ─────────────────────────────────────────────────

    def save_property(self, property_data: dict) -> None:
        """Save a property record."""
        with self.get_session() as session:
            record = session.get(PropertyRecord, property_data["id"])
            if record:
                record.data_json = json.dumps(property_data)
                record.city = property_data.get("city", "")
                record.price = property_data.get("price", 0)
                record.bedrooms = property_data.get("bedrooms", 0)
            else:
                record = PropertyRecord(
                    id=property_data["id"],
                    data_json=json.dumps(property_data),
                    city=property_data.get("city", ""),
                    price=property_data.get("price", 0),
                    bedrooms=property_data.get("bedrooms", 0),
                )
                session.add(record)
            session.commit()

    def get_property(self, property_id: str) -> Optional[dict]:
        """Get a property by ID."""
        with self.get_session() as session:
            record = session.get(PropertyRecord, property_id)
            if not record:
                return None
            return json.loads(record.data_json)


# ── Singleton ────────────────────────────────────────────────────────────────


_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get or create the database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize()
    return _db_manager
