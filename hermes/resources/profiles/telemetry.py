"""
===============================================================================
Hermes Runtime Profile Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeProfileTelemetry:
    """
    Runtime profile usage statistics.
    """

    activations: int = 0

    total_runtime: float = 0.0

    average_runtime: float = 0.0