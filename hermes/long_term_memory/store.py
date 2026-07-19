"""
===============================================================================
Memory Store
===============================================================================

Dependencies:
    - hermes.long_term_memory.models

Consumes:
    - MemoryRecord

Produces:
    - MemoryStore

Public API:
    - MemoryStore

TODO:
    - Implement persistent storage backends (SQLite, JSON).
    - Implement vector database backends (ChromaDB, FAISS).
===============================================================================
"""

from __future__ import annotations

import time
import uuid
from typing import List, Optional

from hermes.long_term_memory.models import MemoryRecord


class MemoryStore:
    """
    Pure in-memory storage for MemoryRecords.
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def add(self, content: str, metadata: Optional[dict] = None) -> MemoryRecord:
        """Add a new record to the store."""
        record_id = uuid.uuid4().hex
        if metadata is None:
            metadata = {}
        record = MemoryRecord(
            id=record_id,
            content=content,
            metadata=metadata,
        )
        self._records[record_id] = record
        return record

    def update(
        self, 
        record_id: str, 
        content: Optional[str] = None, 
        metadata: Optional[dict] = None
    ) -> Optional[MemoryRecord]:
        """
        Update an existing record. Returns None if not found.
        
        Note on metadata: 
        If provided, the metadata dictionary is merged into the existing 
        record's metadata, NOT replaced.
        """
        if record_id not in self._records:
            return None
        
        record = self._records[record_id]
        if content is not None:
            record.content = content
        if metadata is not None:
            record.metadata.update(metadata)
        
        record.updated_at = time.time()
        return record

    def delete(self, record_id: str) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        return self._records.pop(record_id, None) is not None

    def clear(self) -> None:
        """Clear all records."""
        self._records.clear()

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        """Retrieve a record by ID."""
        return self._records.get(record_id)

    def list(self) -> List[MemoryRecord]:
        """List all records, deterministically sorted by creation time."""
        return sorted(self._records.values(), key=lambda r: r.created_at)

    def search(self, query: str) -> List[MemoryRecord]:
        """
        Search records by simple case-insensitive substring match.
        Returns results deterministically sorted by creation time.
        """
        query_lower = query.lower()
        results = [
            r for r in self._records.values() 
            if query_lower in r.content.lower()
        ]
        return sorted(results, key=lambda r: r.created_at)