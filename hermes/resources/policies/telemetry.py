"""
===============================================================================
Hermes Runtime Policy Telemetry
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePolicyTelemetry:

    evaluations: int = 0

    accepted: int = 0

    rejected: int = 0

    average_time: float = 0.0
