"""
===============================================================================
Hermes AI Context

Execution state for an AI request.

AIContext is NOT the request itself.

AIContext is NOT provider metadata.

It stores runtime information only.

It remains generic and reusable for every AI capability.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIContext:
    """
    Runtime context for AI execution.

    This is a generic container for execution state.

    It does not contain business logic.

    It does not know about specific capabilities.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    request_id: str | None = None

    session_id: str | None = None

    user_id: str | None = None

    conversation_id: str | None = None

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    provider: str | None = None

    model: str | None = None

    timeout: float | None = None

    priority: int = 0

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Metadata Access
    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a metadata value.

        Parameters
        ----------
        key : str
            Metadata key.
        value : Any
            Metadata value.
        """

        self.metadata[key] = value

    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a metadata value.

        Parameters
        ----------
        key : str
            Metadata key.
        default : Any, optional
            Default value if key does not exist.

        Returns
        -------
        Any
            The metadata value, or default if not found.
        """

        return self.metadata.get(key, default)

    # ------------------------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a metadata entry.

        Idempotent.

        Parameters
        ----------
        key : str
            Metadata key to remove.
        """

        self.metadata.pop(key, None)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove all metadata entries.
        """

        self.metadata.clear()

    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> AIContext:
        """
        Return a deep independent copy of the context.

        Returns
        -------
        AIContext
            A new context with deeply copied metadata.
        """

        return AIContext(
            request_id=self.request_id,
            session_id=self.session_id,
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            provider=self.provider,
            model=self.model,
            timeout=self.timeout,
            priority=self.priority,
            metadata=deepcopy(self.metadata),
        )

    # ------------------------------------------------------------------

    def update(
        self,
        mapping: dict[str, Any],
    ) -> None:
        """
        Update metadata with key-value pairs.

        Parameters
        ----------
        mapping : dict[str, Any]
            Dictionary of metadata to merge.
        """

        self.metadata.update(mapping)

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Check if a metadata key exists.

        Parameters
        ----------
        key : str
            Metadata key.

        Returns
        -------
        bool
            True if key exists, False otherwise.
        """

        return key in self.metadata

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of metadata entries.

        Returns
        -------
        int
            Metadata count.
        """

        return len(self.metadata)

    # ------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Return True if the context has any metadata.

        Returns
        -------
        bool
            True if metadata is non-empty, False otherwise.
        """

        return bool(self.metadata)
