"""
===============================================================================
Hermes Scheduler Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SchedulerTelemetry:
    """
    Runtime scheduler statistics.
    """

    executions: int = 0

    completed_nodes: int = 0

    failed_nodes: int = 0

    average_runtime: float = 0.0