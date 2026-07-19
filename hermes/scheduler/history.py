"""
===============================================================================
Hermes Scheduler History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class SchedulerHistory:
    """
    Records one scheduler execution.
    """

    graph_nodes: int

    executed_nodes: int

    timestamp: float = field(default_factory=time)

    success: bool = True
