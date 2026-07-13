"""
===============================================================================
Hermes Runtime Scheduler History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class RuntimeSchedulerHistory:
    """
    Scheduler execution history.
    """

    scheduler: str

    timestamp: float = field(default_factory=time)

    duration: float = 0.0

    success: bool = True