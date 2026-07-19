"""
===============================================================================
Hermes Reasoning Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReasoningContext:
    """
    Shared context used throughout the reasoning pipeline.
    """

    prompt: str = ""

    objective: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)
