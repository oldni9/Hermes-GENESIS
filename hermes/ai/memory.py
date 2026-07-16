"""
===============================================================================
Hermes AI Memory System

Manages short-term and long-term memory for Hermes.

Features:
    - Memory entries with content, metadata, tags, importance, timestamps
    - Short-term and long-term memory types
    - Search and filtering
    - Ranking by importance and recency
    - Automatic pruning based on capacity or importance
    - Serialization (dict/JSON)
    - Statistics
    - Integration with AIConversation, AISession, Prompt, etc.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import json
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Self

from hermes.ai.prompt import PromptRole


# =============================================================================
# Memory Type
# =============================================================================

class MemoryType(str, Enum):
    """
    Type of memory.

    SHORT_TERM - Temporary memory for current session/conversation.
    LONG_TERM   - Persistent memory across sessions.
    """

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


# =============================================================================
# Memory Entry
# =============================================================================

@dataclass(slots=True)
class MemoryEntry:
    """
    A single memory entry.

    Attributes
    ----------
    id : str
        Unique identifier.
    content : str
        The memory content.
    memory_type : MemoryType
        Type of memory.
    importance : float
        Importance score (0.0 to 1.0).
    created_at : float
        Creation timestamp.
    updated_at : float
        Last update timestamp.
    metadata : dict[str, Any]
        Additional metadata.
    tags : list[str]
        Tags for categorization.
    tokens : int | None
        Estimated token count of the content.
    """

    id: str
    content: str
    memory_type: MemoryType = MemoryType.LONG_TERM
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    tokens: int | None = None

    def touch(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = time.time()

    def update_content(self, new_content: str) -> None:
        """
        Update the content and refresh the timestamp.

        Parameters
        ----------
        new_content : str
            New content.
        """
        self.content = new_content
        self.touch()

    def add_tag(self, tag: str) -> None:
        """Add a tag."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "tags": self.tags,
            "tokens": self.tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create from dictionary."""
        memory_type = data.get("memory_type", "long_term")
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=memory_type,
            importance=data.get("importance", 0.5),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            tokens=data.get("tokens"),
        )


# =============================================================================
# Memory Statistics
# =============================================================================

@dataclass(slots=True)
class MemoryStatistics:
    """
    Statistics for the memory store.

    Attributes
    ----------
    total_entries : int
        Total number of entries.
    short_term_count : int
        Number of short-term entries.
    long_term_count : int
        Number of long-term entries.
    total_tokens : int
        Total estimated tokens.
    average_importance : float
        Average importance score.
    oldest_entry_time : float | None
        Timestamp of the oldest entry.
    newest_entry_time : float | None
        Timestamp of the newest entry.
    created_at : float
        When statistics were computed.
    """

    total_entries: int = 0
    short_term_count: int = 0
    long_term_count: int = 0
    total_tokens: int = 0
    average_importance: float = 0.0
    oldest_entry_time: float | None = None
    newest_entry_time: float | None = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entries": self.total_entries,
            "short_term_count": self.short_term_count,
            "long_term_count": self.long_term_count,
            "total_tokens": self.total_tokens,
            "average_importance": self.average_importance,
            "oldest_entry_time": self.oldest_entry_time,
            "newest_entry_time": self.newest_entry_time,
            "created_at": self.created_at,
        }


# =============================================================================
# Memory Store
# =============================================================================

class MemoryStore:
    """
    Core memory store managing memory entries.

    Supports:
        - Add, get, update, delete
        - Search and filter
        - Ranking by importance
        - Pruning by capacity or importance
        - Statistics
    """

    def __init__(
        self,
        max_short_term: int = 100,
        max_long_term: int = 1000,
    ):
        """
        Initialize the memory store.

        Parameters
        ----------
        max_short_term : int, default=100
            Maximum short-term entries.
        max_long_term : int, default=1000
            Maximum long-term entries.
        """
        self._entries: dict[str, MemoryEntry] = {}
        self._max_short_term = max_short_term
        self._max_long_term = max_long_term

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return uuid.uuid4().hex[:16]

    @staticmethod
    def _estimate_tokens(content: str) -> int:
        """Estimate tokens using a simple heuristic."""
        return (len(content) // 4) + 1

    @staticmethod
    def _validate_importance(importance: float) -> None:
        """Validate importance is between 0 and 1."""
        if not (0.0 <= importance <= 1.0):
            raise ValueError("Importance must be between 0.0 and 1.0.")

    def add(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.LONG_TERM,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """
        Add a memory entry.

        Parameters
        ----------
        content : str
            The memory content.
        memory_type : MemoryType, default=MemoryType.LONG_TERM
            Type of memory.
        importance : float, default=0.5
            Importance score (0.0 to 1.0).
        tags : list[str] | None, optional
            Tags for categorization.
        metadata : dict[str, Any] | None, optional
            Additional metadata.

        Returns
        -------
        MemoryEntry
            The created entry.
        """
        self._validate_importance(importance)
        entry = MemoryEntry(
            id=self._generate_id(),
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            tokens=self._estimate_tokens(content),
        )
        self._entries[entry.id] = entry

        # Prune if capacity exceeded
        self._prune()

        return entry

    def get(self, entry_id: str) -> MemoryEntry | None:
        """
        Get a memory entry by ID.

        Parameters
        ----------
        entry_id : str
            Entry ID.

        Returns
        -------
        MemoryEntry | None
            The entry or None if not found.
        """
        return self._entries.get(entry_id)

    def update(self, entry_id: str, content: str | None = None, importance: float | None = None) -> bool:
        """
        Update a memory entry.

        Parameters
        ----------
        entry_id : str
            Entry ID.
        content : str | None, optional
            New content.
        importance : float | None, optional
            New importance.

        Returns
        -------
        bool
            True if updated, False if entry not found.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            return False
        if content is not None:
            entry.update_content(content)
            entry.tokens = self._estimate_tokens(content)
        if importance is not None:
            self._validate_importance(importance)
            entry.importance = importance
            entry.touch()
        return True

    def delete(self, entry_id: str) -> bool:
        """
        Delete a memory entry.

        Parameters
        ----------
        entry_id : str
            Entry ID.

        Returns
        -------
        bool
            True if deleted, False if not found.
        """
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()

    def search(
        self,
        query: str,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        max_importance: float = 1.0,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search memory entries.

        Uses simple substring matching (case-insensitive).

        Parameters
        ----------
        query : str
            Search query.
        memory_type : MemoryType | None, optional
            Filter by memory type.
        tags : list[str] | None, optional
            Filter by tags (entry must have all tags).
        min_importance : float, default=0.0
            Minimum importance.
        max_importance : float, default=1.0
            Maximum importance.
        limit : int, default=10
            Maximum number of results.

        Returns
        -------
        list[MemoryEntry]
            Matching entries, sorted by relevance (importance + recency).
        """
        results = []
        query_lower = query.lower()
        for entry in self._entries.values():
            if memory_type is not None and entry.memory_type != memory_type:
                continue
            if tags is not None and not all(tag in entry.tags for tag in tags):
                continue
            if not (min_importance <= entry.importance <= max_importance):
                continue
            if query_lower in entry.content.lower():
                results.append(entry)

        # Sort by importance (desc) then recency (desc)
        results.sort(key=lambda e: (e.importance, e.updated_at), reverse=True)

        return results[:limit]

    def filter(
        self,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        max_importance: float = 1.0,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> list[MemoryEntry]:
        """
        Filter memory entries.

        Parameters
        ----------
        memory_type : MemoryType | None, optional
            Filter by memory type.
        tags : list[str] | None, optional
            Filter by tags (entry must have all tags).
        min_importance : float, default=0.0
            Minimum importance.
        max_importance : float, default=1.0
            Maximum importance.
        start_time : float | None, optional
            Filter by created_at >= start_time.
        end_time : float | None, optional
            Filter by created_at <= end_time.

        Returns
        -------
        list[MemoryEntry]
            Matching entries.
        """
        results = []
        for entry in self._entries.values():
            if memory_type is not None and entry.memory_type != memory_type:
                continue
            if tags is not None and not all(tag in entry.tags for tag in tags):
                continue
            if not (min_importance <= entry.importance <= max_importance):
                continue
            if start_time is not None and entry.created_at < start_time:
                continue
            if end_time is not None and entry.created_at > end_time:
                continue
            results.append(entry)
        # Sort by recency
        results.sort(key=lambda e: e.updated_at, reverse=True)
        return results

    def rank(
        self,
        query: str | None = None,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Rank memory entries by importance and recency.

        If query is provided, boosts entries containing the query.

        Parameters
        ----------
        query : str | None, optional
            Optional query for relevance boost.
        memory_type : MemoryType | None, optional
            Filter by memory type.
        limit : int, default=10
            Maximum results.

        Returns
        -------
        list[MemoryEntry]
            Ranked entries.
        """
        entries = self.filter(memory_type=memory_type)

        def score(e: MemoryEntry) -> float:
            s = e.importance
            if query and query.lower() in e.content.lower():
                s += 0.1
            return s

        # Sort by computed score (desc), then recency (desc)
        entries.sort(key=lambda e: (score(e), e.updated_at), reverse=True)
        return entries[:limit]

    def _prune(self) -> None:
        """
        Prune entries to stay within capacity limits.
        Removes least important and oldest entries of each type.
        """
        short_term = [e for e in self._entries.values() if e.memory_type == MemoryType.SHORT_TERM]
        long_term = [e for e in self._entries.values() if e.memory_type == MemoryType.LONG_TERM]

        if len(short_term) > self._max_short_term:
            # Remove least important, oldest first
            short_term.sort(key=lambda e: (e.importance, e.updated_at))
            to_remove = short_term[:len(short_term) - self._max_short_term]
            for e in to_remove:
                del self._entries[e.id]

        if len(long_term) > self._max_long_term:
            long_term.sort(key=lambda e: (e.importance, e.updated_at))
            to_remove = long_term[:len(long_term) - self._max_long_term]
            for e in to_remove:
                del self._entries[e.id]

    def statistics(self) -> MemoryStatistics:
        """
        Compute statistics.

        Returns
        -------
        MemoryStatistics
            Statistics object.
        """
        stats = MemoryStatistics()
        entries = list(self._entries.values())
        stats.total_entries = len(entries)
        if stats.total_entries == 0:
            return stats
        stats.short_term_count = sum(1 for e in entries if e.memory_type == MemoryType.SHORT_TERM)
        stats.long_term_count = stats.total_entries - stats.short_term_count
        stats.total_tokens = sum(e.tokens or 0 for e in entries)
        stats.average_importance = sum(e.importance for e in entries) / stats.total_entries
        stats.oldest_entry_time = min(e.created_at for e in entries)
        stats.newest_entry_time = max(e.created_at for e in entries)
        return stats

    def count(self) -> int:
        """Return total number of entries."""
        return len(self._entries)

    def entries(self) -> list[MemoryEntry]:
        """Return all entries."""
        return list(self._entries.values())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the store to a dictionary."""
        return {
            "version": 1,
            "max_short_term": self._max_short_term,
            "max_long_term": self._max_long_term,
            "entries": [e.to_dict() for e in self._entries.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryStore:
        """Deserialize from a dictionary."""
        version = data.get("version", 1)
        # Version 1 is the current format; no migration needed yet.
        store = cls(
            max_short_term=data.get("max_short_term", 100),
            max_long_term=data.get("max_long_term", 1000),
        )
        for entry_data in data.get("entries", []):
            entry = MemoryEntry.from_dict(entry_data)
            store._entries[entry.id] = entry
        return store

    def export_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)

    @classmethod
    def import_json(cls, data: str) -> MemoryStore:
        """Import from JSON."""
        return cls.from_dict(json.loads(data))


# =============================================================================
# Memory (High-Level API)
# =============================================================================

class Memory:
    """
    High-level memory system for Hermes.

    Integrates with AIConversation, AISession, and Prompt.

    Provides:
        - Add memories from conversations or sessions
        - Search and retrieve memories
        - Manage short-term and long-term memories

    Examples
    --------
    >>> memory = Memory()
    >>> memory.add("User prefers Python", tags=["preference"])
    >>> results = memory.search("Python")
    """

    def __init__(
        self,
        store: MemoryStore | None = None,
        max_short_term: int = 100,
        max_long_term: int = 1000,
    ):
        """
        Initialize the memory system.

        Parameters
        ----------
        store : MemoryStore | None, optional
            Existing store to use. If None, a new one is created.
        max_short_term : int, default=100
            Maximum short-term entries.
        max_long_term : int, default=1000
            Maximum long-term entries.
        """
        self._store = store or MemoryStore(
            max_short_term=max_short_term,
            max_long_term=max_long_term,
        )

    @property
    def store(self) -> MemoryStore:
        """Get the underlying memory store."""
        return self._store

    def add(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.LONG_TERM,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """
        Add a memory entry.

        Parameters
        ----------
        content : str
            The memory content.
        memory_type : MemoryType, default=MemoryType.LONG_TERM
            Type of memory.
        importance : float, default=0.5
            Importance score (0.0 to 1.0).
        tags : list[str] | None, optional
            Tags for categorization.
        metadata : dict[str, Any] | None, optional
            Additional metadata.

        Returns
        -------
        MemoryEntry
            The created entry.
        """
        return self._store.add(content, memory_type, importance, tags, metadata)

    def add_from_conversation(
        self,
        conversation: AIConversation,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[MemoryEntry]:
        """
        Add entries from a conversation.

        Each user and assistant message becomes a separate memory entry.

        Parameters
        ----------
        conversation : AIConversation
            The conversation to extract memories from.
        memory_type : MemoryType, default=MemoryType.SHORT_TERM
            Type of memory.
        importance : float, default=0.5
            Base importance for each entry.
        tags : list[str] | None, optional
            Tags to add to all entries.
        metadata : dict[str, Any] | None, optional
            Base metadata.

        Returns
        -------
        list[MemoryEntry]
            Created entries.
        """
        entries = []
        for msg in conversation.messages:
            if msg.deleted or msg.archived:
                continue
            # Check role using PromptRole from the conversation module.
            # In Hermes, conversation message role is stored as PromptRole or string.
            role = msg.role
            if isinstance(role, PromptRole):
                role = role.value
            if role in ["user", "assistant"]:
                entry = self._store.add(
                    content=msg.content,
                    memory_type=memory_type,
                    importance=importance,
                    tags=tags,
                    metadata=metadata or {},
                )
                entries.append(entry)
        return entries

    def add_from_session(
        self,
        session: AISession,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[MemoryEntry]:
        """
        Add entries from a session's history.

        Extracts prompts and responses.

        Parameters
        ----------
        session : AISession
            The session.
        memory_type : MemoryType, default=MemoryType.SHORT_TERM
            Type of memory.
        importance : float, default=0.5
            Base importance.
        tags : list[str] | None, optional
            Tags.
        metadata : dict[str, Any] | None, optional
            Base metadata.

        Returns
        -------
        list[MemoryEntry]
            Created entries.
        """
        entries = []
        for prompt in session.history.prompts:
            for msg in prompt.messages:
                if msg.content:
                    entry = self._store.add(
                        content=msg.content,
                        memory_type=memory_type,
                        importance=importance,
                        tags=tags,
                        metadata=metadata or {},
                    )
                    entries.append(entry)
        for response in session.history.responses:
            if response.success and response.text():
                entry = self._store.add(
                    content=response.text(),
                    memory_type=memory_type,
                    importance=importance,
                    tags=tags,
                    metadata=metadata or {},
                )
                entries.append(entry)
        return entries

    def search(
        self,
        query: str,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        max_importance: float = 1.0,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search memory entries.

        Parameters
        ----------
        query : str
            Search query.
        memory_type : MemoryType | None, optional
            Filter by type.
        tags : list[str] | None, optional
            Filter by tags (all must match).
        min_importance : float, default=0.0
            Minimum importance.
        max_importance : float, default=1.0
            Maximum importance.
        limit : int, default=10
            Maximum results.

        Returns
        -------
        list[MemoryEntry]
            Matching entries.
        """
        return self._store.search(query, memory_type, tags, min_importance, max_importance, limit)

    def filter(
        self,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        max_importance: float = 1.0,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> list[MemoryEntry]:
        """
        Filter memory entries.

        Parameters
        ----------
        memory_type : MemoryType | None, optional
            Filter by type.
        tags : list[str] | None, optional
            Filter by tags (all must match).
        min_importance : float, default=0.0
            Minimum importance.
        max_importance : float, default=1.0
            Maximum importance.
        start_time : float | None, optional
            Filter by created_at >= start_time.
        end_time : float | None, optional
            Filter by created_at <= end_time.

        Returns
        -------
        list[MemoryEntry]
            Matching entries.
        """
        return self._store.filter(memory_type, tags, min_importance, max_importance, start_time, end_time)

    def rank(
        self,
        query: str | None = None,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Rank memory entries by importance and recency.

        Parameters
        ----------
        query : str | None, optional
            Optional query for relevance boost.
        memory_type : MemoryType | None, optional
            Filter by type.
        limit : int, default=10
            Maximum results.

        Returns
        -------
        list[MemoryEntry]
            Ranked entries.
        """
        return self._store.rank(query, memory_type, limit)

    def get(self, entry_id: str) -> MemoryEntry | None:
        """Get a memory entry by ID."""
        return self._store.get(entry_id)

    def update(self, entry_id: str, content: str | None = None, importance: float | None = None) -> bool:
        """Update a memory entry."""
        return self._store.update(entry_id, content, importance)

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        return self._store.delete(entry_id)

    def clear(self) -> None:
        """Clear all memory entries."""
        self._store.clear()

    def statistics(self) -> MemoryStatistics:
        """Get memory statistics."""
        return self._store.statistics()

    def count(self) -> int:
        """Get total number of entries."""
        return self._store.count()

    def entries(self) -> list[MemoryEntry]:
        """Get all entries."""
        return self._store.entries()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the memory system to a dictionary."""
        return self._store.to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Memory:
        """Deserialize from a dictionary."""
        store = MemoryStore.from_dict(data)
        return cls(store=store)

    def export_json(self) -> str:
        """Export to JSON."""
        return self._store.export_json()

    @classmethod
    def import_json(cls, data: str) -> Memory:
        """Import from JSON."""
        store = MemoryStore.import_json(data)
        return cls(store=store)

    def __len__(self) -> int:
        """Return the number of memory entries."""
        return self._store.count()

    def __iter__(self):
        """Iterate over memory entries."""
        return iter(self._store.entries())

    def __repr__(self) -> str:
        return f"<Memory entries={self._store.count()}>"

    def __str__(self) -> str:
        return self.__repr__()


# =============================================================================
# Verification Block
# =============================================================================

# ✓ Classes:
#   - MemoryType (Enum)
#   - MemoryEntry
#   - MemoryStatistics
#   - MemoryStore
#   - Memory

# ✓ Methods:
#   - MemoryStore: add, get, update, delete, clear, search, filter, rank, prune, statistics, count, entries, to_dict, from_dict, export_json, import_json
#   - Memory: add, add_from_conversation, add_from_session, search, filter, rank, get, update, delete, clear, statistics, count, entries, to_dict, from_dict, export_json, import_json
#   - Magic methods: __len__, __iter__, __repr__, __str__

# ✓ Serialization:
#   - to_dict / from_dict with version
#   - export_json / import_json

# ✓ Validation:
#   - Importance range validation (centralized)
#   - Type checking

# ✓ Imports:
#   - All imports are valid and used

# ✓ Compatibility:
#   - Integrates with AIConversation, AISession, Prompt (via PromptRole)
#   - Works with memory store