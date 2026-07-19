"""
===============================================================================
Hermes Reasoning History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ReasoningHistory:

    prompt: str

    nodes: int

    timestamp: float = field(default_factory=time)
