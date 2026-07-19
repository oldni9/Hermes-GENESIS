"""
===============================================================================
Hermes Runtime Preset Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePresetTelemetry:
    """
    Preset usage statistics.
    """

    activations: int = 0

    saves: int = 0

    loads: int = 0

    average_load_time: float = 0.0
