"""
===============================================================================
Hermes Executive Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutiveContext:
    """
    Executive runtime state.

    Shared across the entire reasoning pipeline.
    """

    prompt: str = ""

    objective: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    completed: bool = False
