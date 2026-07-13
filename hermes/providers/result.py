"""
===============================================================================
Hermes Provider Result

Universal provider response.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderResult:
    """
    Provider-independent response object.
    """

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    success: bool

    # ------------------------------------------------------------------
    # Generated content
    # ------------------------------------------------------------------

    text: str = ""

    # ------------------------------------------------------------------
    # Optional outputs
    # ------------------------------------------------------------------

    images: list[Any] = field(
        default_factory=list,
    )

    audio: Any | None = None

    embeddings: list[float] = field(
        default_factory=list,
    )

    # ------------------------------------------------------------------
    # Tool calling
    # ------------------------------------------------------------------

    tool_calls: list[Any] = field(
        default_factory=list,
    )

    # ------------------------------------------------------------------
    # Usage
    # ------------------------------------------------------------------

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    finish_reason: str | None = None

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------

    error: str | None = None

    # ------------------------------------------------------------------
    # Raw provider response
    # ------------------------------------------------------------------

    raw: Any | None = None