"""
===============================================================================
Hermes Runtime Pipeline Telemetry

Pipeline execution statistics.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePipelineTelemetry:

    executions: int = 0

    failures: int = 0

    total_time: float = 0.0

    average_time: float = 0.0
