"""
===============================================================================
Hermes Runtime Scheduler Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeSchedulerTelemetry:
    """
    Scheduler statistics.
    """

    executions: int = 0

    total_time: float = 0.0

    average_time: float = 0.0

    failures: int = 0