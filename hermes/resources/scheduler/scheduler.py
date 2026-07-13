"""
===============================================================================
Hermes Runtime Scheduler

Represents a Runtime Scheduler configuration.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeScheduler:
    """
    Runtime scheduler configuration.

    A scheduler defines HOW Hermes chooses
    models, providers and execution pipelines.
    """

    name: str

    enabled: bool = True

    strategy: str = "priority"

    allow_parallel: bool = False

    max_parallel_tasks: int = 1

    metadata: dict = field(default_factory=dict)