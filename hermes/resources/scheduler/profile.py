"""
===============================================================================
Hermes Runtime Scheduler Profile

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeSchedulerProfile:
    """
    Scheduler profile.
    """

    name: str

    scheduler: str

    enabled: bool = True