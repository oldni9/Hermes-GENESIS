"""
===============================================================================
Hermes Scheduler Loader
===============================================================================

Loads Scheduler Runtime Objects.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .policy import SchedulerPolicy


class SchedulerLoader:
    """
    Loads Scheduler Policies.
    """

    def load(
        self,
        directory: Path,
    ) -> list[SchedulerPolicy]:

        # JSON loading arrives in Runtime Object Phase 2

        return []
