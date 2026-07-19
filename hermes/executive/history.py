"""
===============================================================================
Hermes Executive History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ExecutiveHistory:
    """
    Stores one executive execution.
    """

    prompt: str

    decision: str

    timestamp: float = field(default_factory=time)

    success: bool = True
