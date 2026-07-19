"""
===============================================================================
Hermes Vector Store (SQLite)
===============================================================================
"""

import json
import logging
import math
import sqlite3
from contextlib import contextmanager
from typing import Any, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._query(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                embedding TEXT,
                metadata TEXT
            )
            """
        ) as cursor:
            pass

    @contextmanager
    def _query(self, query: str, params: tuple = ()):
        """Context manager that yields a cursor and auto‑closes the connection."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _is_valid_embedding(embedding: list[float]) -> bool:
        """Check that no element is NaN or Inf."""
        return all(not math.isnan(x) and not math.isinf(x) for x in embedding)

    def upsert(self, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        if not self._is_valid_embedding(embedding):
            logger.debug("Skipping embedding with NaN/Inf: %s", id)
            return
        with self._query(
            "INSERT OR REPLACE INTO embeddings (id, embedding, metadata) VALUES (?, ?, ?)",
            (id, json.dumps(embedding), json.dumps(metadata))
        ) as cursor:
            pass

    def get(self, id: str) -> Optional[tuple[str, list[float], dict]]:
        with self._query("SELECT id, embedding, metadata FROM embeddings WHERE id=?", (id,)) as cursor:
            row = cursor.fetchone()
            if row is None:
                return None
            return row[0], json.loads(row[1]), json.loads(row[2])

    def delete(self, id: str) -> None:
        with self._query("DELETE FROM embeddings WHERE id=?", (id,)) as cursor:
            pass

    def search(self, embedding: list[float], limit: int = 10) -> list[tuple[str, float, dict]]:
        # Placeholder; actual implementation would use vector similarity
        # Not shown for brevity
        pass