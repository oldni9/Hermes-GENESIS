"""
===============================================================================
Hermes Runtime Model
===============================================================================

Represents one LLM inside Hermes.

Models are Runtime Objects.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeModel:
    """
    Runtime representation of an AI model.
    """

    # Unique id
    id: str

    # Display name
    name: str

    # Provider id
    provider: str

    # Model identifier used by provider
    model: str

    # Can Hermes use this model?
    enabled: bool = True

    # User configurable priority
    priority: int = 100

    # Context window
    context_window: int = 8192

    # Estimated latency (ms)
    latency: float = 0.0

    # Relative cost
    cost: float = 0.0

    # Trust score
    trust: float = 1.0

    # Capability tags
    capabilities: list[str] = field(default_factory=list)

    # Optional metadata
    metadata: dict = field(default_factory=dict)