"""
===============================================================================
SQLite Store
===============================================================================

Dependencies:
    - sqlite3
    - json
    - threading
    - time
    - uuid
    - typing
    - hermes.long_term_memory.models

Consumes:
    - MemoryRecord

Produces:
    - SQLiteStore

Public API:
    - SQLiteStore

Note: 
SQLiteStore implements the same interface as MemoryStore (structural subtyping).
It does not inherit from MemoryStore because MemoryStore is a concrete implementation 
that initializes its own in-memory state, and we want to avoid modifying the 
core MemoryManager to support an ABC refactor.

TODO (Future PRs):
    - Introduce a MemoryStoreProtocol to formalize structural subtyping.
    - Add full-text search (FTS5) for better search performance.
    - Add vector storage for semantic search.
    - Expose workspace_id filtering.
    - Rename `list` to `list_records` to avoid shadowing builtins.
    - Extract migrations into a dedicated folder/module.
===============================================================================
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from typing import List, Optional

from hermes.long_term_memory.models import MemoryRecord


class SQLiteStore:
    """
    SQLite implementation of the MemoryStore interface.
    Provides durable, persistent storage for MemoryRecords.
    """
    
    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._lock = threading.RLock()  # RLock allows nested calls from the same thread
        self._conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        
        self._apply_pragmas()
        self._migrate()

    def _apply_pragmas(self) -> None:
        """
        Apply SQLite PRAGMAs for performance and concurrency.
        - WAL: Write-Ahead Logging allows concurrent reads during writes.
        - foreign_keys: Enforce foreign key constraints.
        """
        with self._lock:
            # WAL is only supported for file-backed databases
            if self._db_path != ":memory:":
                self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA foreign_keys=ON;")

    def _migrate(self) -> None:
        """
        Run database migrations.
        Currently supports version 1: initial schema creation.
        """
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at REAL NOT NULL
                );
            """)
            
            cursor = self._conn.execute("SELECT MAX(version) FROM schema_migrations;")
            row = cursor.fetchone()
            current_version = row[0] if row and row[0] is not None else 0

            if current_version < 1:
                self._conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_records (
                        id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL DEFAULT 'default',
                        content TEXT NOT NULL,
                        metadata TEXT NOT NULL DEFAULT '{}',
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    );
                """)
                self._conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_workspace ON memory_records(workspace_id);")
                self._conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_content ON memory_records(content);")
                self._conn.execute("INSERT INTO schema_migrations (version, applied_at) VALUES (1, ?);", (time.time(),))
                self._conn.commit()

    def _check_closed(self) -> None:
        """Ensure the connection is active before performing operations."""
        if self._conn is None:
            raise RuntimeError("SQLiteStore has been closed.")

    def _serialize_metadata(self, metadata: dict) -> str:
        """Safely serialize metadata to JSON, handling non-serializable types."""
        return json.dumps(metadata, default=str)

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            content=row["content"],
            metadata=json.loads(row["metadata"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def __enter__(self) -> "SQLiteStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def add(self, content: str, metadata: Optional[dict] = None) -> MemoryRecord:
        self._check_closed()
        record_id = uuid.uuid4().hex
        if metadata is None:
            metadata = {}
        current_time = time.time()
        metadata_str = self._serialize_metadata(metadata)
        
        with self._lock:
            self._conn.execute(
                "INSERT INTO memory_records (id, content, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?);",
                (record_id, content, metadata_str, current_time, current_time)
            )
            self._conn.commit()
            
        return MemoryRecord(
            id=record_id,
            content=content,
            metadata=metadata,
            created_at=current_time,
            updated_at=current_time
        )

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
        self._check_closed()
        with self._lock:
            cursor = self._conn.execute("SELECT * FROM memory_records WHERE id = ?;", (record_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            current_metadata = json.loads(row["metadata"])
            new_content = content if content is not None else row["content"]
            if metadata is not None:
                current_metadata.update(metadata)
            new_metadata_str = self._serialize_metadata(current_metadata)
            new_updated_at = time.time()
            
            self._conn.execute(
                "UPDATE memory_records SET content = ?, metadata = ?, updated_at = ? WHERE id = ?;",
                (new_content, new_metadata_str, new_updated_at, record_id)
            )
            self._conn.commit()
            
            return MemoryRecord(
                id=record_id,
                content=new_content,
                metadata=current_metadata,
                created_at=row["created_at"],
                updated_at=new_updated_at
            )

    def delete(self, record_id: str) -> bool:
        self._check_closed()
        with self._lock:
            cursor = self._conn.execute("DELETE FROM memory_records WHERE id = ?;", (record_id,))
            self._conn.commit()
            return cursor.rowcount > 0

    def clear(self) -> None:
        self._check_closed()
        with self._lock:
            self._conn.execute("DELETE FROM memory_records;")
            self._conn.commit()

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        self._check_closed()
        with self._lock:
            cursor = self._conn.execute("SELECT * FROM memory_records WHERE id = ?;", (record_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_record(row)

    def list(self) -> List[MemoryRecord]:
        self._check_closed()
        with self._lock:
            cursor = self._conn.execute("SELECT * FROM memory_records ORDER BY created_at ASC;")
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def search(self, query: str) -> List[MemoryRecord]:
        self._check_closed()
        # FIX: Escape LIKE wildcards to allow literal searches for % and _
        escaped_query = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like_query = f"%{escaped_query.lower()}%"
        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM memory_records WHERE lower(content) LIKE ? ESCAPE '\\' ORDER BY created_at ASC;",
                (like_query,)
            )
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None