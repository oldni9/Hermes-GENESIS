"""
===============================================================================
Hermes Provider Request

Universal request object passed to every provider.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderRequest:
    """
    Provider-independent inference request.

    Every provider receives exactly this object.
    """

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    prompt: str

    # ------------------------------------------------------------------
    # Optional routing
    # ------------------------------------------------------------------

    model: str | None = None

    system_prompt: str | None = None

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    temperature: float = 0.7

    top_p: float = 1.0

    max_tokens: int | None = None

    stop: list[str] = field(
        default_factory=list,
    )

    stream: bool = False

    # ------------------------------------------------------------------
    # Multimodal
    # ------------------------------------------------------------------

    images: list[Any] = field(
        default_factory=list,
    )

    audio: Any | None = None

    video: Any | None = None

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    tools: list[Any] = field(
        default_factory=list,
    )

    tool_choice: str | None = None

    # ------------------------------------------------------------------
    # Provider specific extras
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
