"""
===============================================================================
Hermes Session Manager

Abstract interface for session storage and lifecycle management.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hermes.ai.session import AISession


class SessionManager(ABC):
    """Abstract interface for session management."""

    @abstractmethod
    def create(
        self,
        provider: str | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> AISession:
        """Create a new session."""
        ...

    @abstractmethod
    def get(self, session_id: str) -> AISession | None:
        """Retrieve a session by ID."""
        ...

    @abstractmethod
    def close(self, session_id: str) -> None:
        """Close and remove a session."""
        ...

    @abstractmethod
    def list(self) -> list[AISession]:
        """List all active sessions."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the number of active sessions."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Close and remove all sessions."""
        ...


class MemorySessionManager(SessionManager):
    """In-memory implementation of SessionManager."""

    def __init__(self) -> None:
        self._sessions: dict[str, AISession] = {}

    def create(
        self,
        provider: str | None = None,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> AISession:
        session = AISession(
            provider=provider,
            model=model,
            metadata=metadata,
            tags=tags,
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> AISession | None:
        return self._sessions.get(session_id)

    def close(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session is not None:
            session.close()

    def list(self) -> list[AISession]:
        return list(self._sessions.values())

    def count(self) -> int:
        return len(self._sessions)

    def clear(self) -> None:
        for session in list(self._sessions.values()):
            session.close()
        self._sessions.clear()