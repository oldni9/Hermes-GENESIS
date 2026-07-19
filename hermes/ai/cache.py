"""
===============================================================================
Hermes AI Cache

Stores AI responses in memory.

Provider-independent.

Model-independent.

Does NOT perform AI.

Does NOT know about OCR, Vision, Speech or Embeddings.

Simply stores and retrieves cached AIResponse objects.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from time import time
from typing import Any

from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


@dataclass(slots=True)
class CacheEntry:
    """
    Internal cache entry.

    Stores a response with creation and expiration timestamps.
    """

    key: str

    response: AIResponse

    created_at: float = field(default_factory=time)

    expires_at: float | None = None


class AICache:
    """
    In-memory cache for AI responses.

    The cache stores AIResponse objects by deterministic key.

    It does not execute providers.

    It does not know about capabilities.

    It only stores and retrieves.
    """

    def __init__(self) -> None:
        """
        Initialize empty cache.
        """

        self._entries: dict[str, CacheEntry] = {}

    # ------------------------------------------------------------------

    @staticmethod
    def _make_key(
        request: AIRequest,
    ) -> str:
        """
        Generate a deterministic cache key from a request.

        The key is based on:
            - task
            - input (serialized consistently)
            - options
            - metadata

        Never uses Python hash().

        Parameters
        ----------
        request : AIRequest
            The request to generate a key for.

        Returns
        -------
        str
            SHA256 hex digest.
        """

        # Build a stable dictionary of key components
        components: dict[str, Any] = {
            "task": request.task,
            "input": request.input,
            "options": request.options,
            "metadata": request.metadata,
        }

        # Serialize to JSON for deterministic hashing
        data = json.dumps(
            components,
            sort_keys=True,
            default=str,
        )

        # Generate SHA256 hash
        return hashlib.sha256(
            data.encode("utf-8"),
        ).hexdigest()

    # ------------------------------------------------------------------

    @staticmethod
    def _expired(
        entry: CacheEntry,
    ) -> bool:
        """
        Check if a cache entry has expired.

        Parameters
        ----------
        entry : CacheEntry
            The entry to check.

        Returns
        -------
        bool
            True if expired, False otherwise.
        """

        if entry.expires_at is None:
            return False

        return time() > entry.expires_at

    # ------------------------------------------------------------------

    def store(
        self,
        request: AIRequest,
        response: AIResponse,
        ttl: float | None = None,
    ) -> str:
        """
        Store a response in the cache.

        Parameters
        ----------
        request : AIRequest
            The request that generated the response.
        response : AIResponse
            The response to cache.
        ttl : float | None, optional
            Time-to-live in seconds. None means never expire.

        Returns
        -------
        str
            The cache key.
        """

        key = self._make_key(request)

        expires_at: float | None = None

        if ttl is not None:
            expires_at = time() + ttl

        self._entries[key] = CacheEntry(
            key=key,
            response=response,
            expires_at=expires_at,
        )

        return key

    # ------------------------------------------------------------------

    def get(
        self,
        request: AIRequest,
    ) -> AIResponse | None:
        """
        Retrieve a cached response.

        Returns None if:
            - Key does not exist
            - Entry has expired

        Expired entries are automatically removed.

        Parameters
        ----------
        request : AIRequest
            The request to look up.

        Returns
        -------
        AIResponse | None
            The cached response, or None if not found or expired.
        """

        key = self._make_key(request)

        entry = self._entries.get(key)

        if entry is None:
            return None

        if self._expired(entry):
            self._entries.pop(key, None)
            return None

        return entry.response

    # ------------------------------------------------------------------

    def exists(
        self,
        request: AIRequest,
    ) -> bool:
        """
        Check if a valid cache entry exists.

        Returns False if:
            - Key does not exist
            - Entry has expired

        Expired entries are automatically removed.

        Parameters
        ----------
        request : AIRequest
            The request to check.

        Returns
        -------
        bool
            True if valid cache entry exists, False otherwise.
        """

        key = self._make_key(request)

        entry = self._entries.get(key)

        if entry is None:
            return False

        if self._expired(entry):
            self._entries.pop(key, None)
            return False

        return True

    # ------------------------------------------------------------------

    def remove(
        self,
        request: AIRequest,
    ) -> None:
        """
        Remove an entry from the cache.

        Idempotent.

        Parameters
        ----------
        request : AIRequest
            The request to remove.
        """

        key = self._make_key(request)

        self._entries.pop(key, None)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove every entry from the cache.
        """

        self._entries.clear()

    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> int:
        """
        Remove every expired entry.

        Returns
        -------
        int
            Number of entries removed.
        """

        expired: list[str] = []

        for key, entry in tuple(self._entries.items()):

            if self._expired(entry):
                expired.append(key)

        for key in expired:
            self._entries.pop(key, None)

        return len(expired)

    # ------------------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Return the number of valid (non-expired) entries.

        Does NOT mutate the cache.

        Returns
        -------
        int
            Number of valid cache entries.
        """

        return sum(1 for entry in self._entries.values() if not self._expired(entry))

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of valid cache entries.
        """

        return self.count()

    # ------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Return True if the cache has at least one valid entry.
        """

        return self.count() > 0
