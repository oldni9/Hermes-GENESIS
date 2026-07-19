"""
===============================================================================
Hermes Scheduler Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.scheduler.history import SchedulerHistory


class SchedulerRegistry:
    """
    Stores scheduler execution history.
    """

    def __init__(self) -> None:

        self._history: list[SchedulerHistory] = []

    # ------------------------------------------------------------------

    def add(
        self,
        history: SchedulerHistory,
    ) -> None:

        self._history.append(history)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[SchedulerHistory]:

        return list(self._history)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._history.clear()
