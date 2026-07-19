"""
===============================================================================
Hermes SQLite Memory Backend
===============================================================================
"""
from __future__ import annotations

import copy
import json
import sqlite3
import time
import uuid
from typing import Any, Dict, Mapping, Optional, Self, Tuple

from .backend import MemoryBackend, MemoryCapabilities
from .models import MemoryEntry
from .exceptions import MemoryError, MemoryBackendError


class SQLiteBackend(MemoryBackend):
    """
    SQLite-backed implementation of MemoryBackend.
    Uses the standard library sqlite3 module.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize()

    def _initialize(self) -> None:
        """Create tables if they don't exist."""
        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    tags TEXT,
                    timestamp REAL NOT NULL,
                    score REAL DEFAULT 1.0,
                    metadata TEXT
                )
                """
            )

    def _serialize_tags(self, tags: Tuple[str, ...]) -> str:
        return json.dumps(tags)

    def _deserialize_tags(self, data: Optional[str]) -> Tuple[str, ...]:
        if data is None:
            return ()
        return tuple(json.loads(data))

    def _serialize_metadata(self, metadata: Mapping[str, Any]) -> str:
        return json.dumps(metadata, default=str)

    def _deserialize_metadata(self, data: Optional[str]) -> Dict[str, Any]:
        if data is None:
            return {}
        return json.loads(data)

    @property
    def capabilities(self) -> MemoryCapabilities:
        return MemoryCapabilities(
            persistent=True,
            semantic_search=False,
            delete=True,
            metadata_filtering=False,
        )

    def add(self, entry: MemoryEntry) -> str:
        """Add a memory entry. The backend generates the ID and timestamp."""
        # Deep copy metadata to preserve true immutability
        new_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=entry.content,
            tags=entry.tags,
            timestamp=time.time(),
            score=entry.score,
            metadata=copy.deepcopy(dict(entry.metadata)),
        )
        tags_json = self._serialize_tags(new_entry.tags)
        metadata_json = self._serialize_metadata(new_entry.metadata)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO memory_entries (id, content, tags, timestamp, score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (new_entry.id, new_entry.content, tags_json, new_entry.timestamp, new_entry.score, metadata_json),
            )
        return new_entry.id

    def _search_impl(self, query: str, limit: int) -> list[MemoryEntry]:
        """Internal search implementation (isolated for future replacement)."""
        with self._connection:
            cursor = self._connection.execute(
                """
                SELECT id, content, tags, timestamp, score, metadata
                FROM memory_entries
                WHERE LOWER(content) LIKE ?
                ORDER BY score DESC, timestamp DESC
                LIMIT ?
                """,
                (f"%{query.lower()}%", limit),
            )
            rows = cursor.fetchall()
            entries = []
            for row in rows:
                entries.append(
                    MemoryEntry(
                        id=row["id"],
                        content=row["content"],
                        tags=self._deserialize_tags(row["tags"]),
                        timestamp=row["timestamp"],
                        score=row["score"],
                        metadata=self._deserialize_metadata(row["metadata"]),
                    )
                )
            return entries

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        return self._search_impl(query, limit)

    def count(self) -> int:
        with self._connection:
            cursor = self._connection.execute("SELECT COUNT(*) FROM memory_entries")
            row = cursor.fetchone()
            return row[0] if row else 0

    def delete(self, entry_id: str) -> bool:
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM memory_entries WHERE id = ?",
                (entry_id,),
            )
            return cursor.rowcount > 0

    def clear(self) -> None:
        with self._connection:
            self._connection.execute("DELETE FROM memory_entries")

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()