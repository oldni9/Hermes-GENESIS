"""
===============================================================================
Hermes Subsystem State
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SubsystemState:

    loaded: bool = False

    enabled: bool = True

    healthy: bool = True

    last_error: str = ""