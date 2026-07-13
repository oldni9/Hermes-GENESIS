"""
===============================================================================
Hermes Execution Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionTelemetry:
    """
    Runtime execution statistics.
    """

    executions: int = 0

    successful: int = 0

    failed: int = 0

    average_runtime: float = 0.0