"""
===============================================================================
Hermes Task Builder Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TaskBuilderTelemetry:

    tasks_built: int = 0

    failures: int = 0

    average_runtime: float = 0.0