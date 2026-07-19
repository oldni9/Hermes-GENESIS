"""
===============================================================================
Hermes Executive Decision

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutiveDecision:
    """
    Represents one executive decision.
    """

    prompt: str

    action: str

    confidence: float = 1.0

    metadata: dict[str, Any] = field(default_factory=dict)
