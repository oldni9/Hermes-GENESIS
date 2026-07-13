"""
===============================================================================
Hermes Scheduler Policy
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SchedulerPolicy:
    """
    Runtime scheduler configuration.
    """

    id: str

    name: str

    description: str = ""

    enabled: bool = True

    strategy: str = "balanced"

    allow_parallel: bool = False

    allow_fallback: bool = True

    max_agents: int = 1

    prefer_local: bool = False

    prefer_free: bool = True

    optimize_latency: bool = False

    optimize_quality: bool = True

    optimize_cost: bool = False

    metadata: dict = field(default_factory=dict)