"""
===============================================================================
Hermes Runtime Scheduler Registry
===============================================================================
"""

from __future__ import annotations

from hermes.resources.scheduler.scheduler import RuntimeScheduler


class RuntimeSchedulerRegistry:

    def __init__(self) -> None:

        self._schedulers: dict[str, RuntimeScheduler] = {}

    # --------------------------------------------------------------

    def register(
        self,
        scheduler: RuntimeScheduler,
    ) -> None:

        self._schedulers[scheduler.name] = scheduler

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimeScheduler | None:

        return self._schedulers.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeScheduler]:

        return list(self._schedulers.values())

    # --------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeScheduler]:

        return [
            scheduler for scheduler in self._schedulers.values() if scheduler.enabled
        ]
