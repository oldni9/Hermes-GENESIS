"""
===============================================================================
Hermes AI Execution Plan

Immutable execution plan for a single AI request.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from hermes.ai.orchestrator.constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_USE_CACHE,
)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """
    Immutable execution plan for a single AI request.

    Contains all execution parameters needed by the orchestrator.
    """

    # ------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------

    provider: str | None = None
    model: str | None = None

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    timeout: float = DEFAULT_TIMEOUT

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    use_cache: bool = DEFAULT_USE_CACHE
    cache_ttl: float | None = None

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------

    options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def with_options(self, **kwargs) -> ExecutionPlan:
        """Return a copy with updated options."""
        return replace(self, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "use_cache": self.use_cache,
            "cache_ttl": self.cache_ttl,
            "options": self.options,
            "metadata": self.metadata,
        }