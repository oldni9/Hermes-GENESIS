"""
===============================================================================
Hermes Runtime Scheduler Selector
===============================================================================
"""

from __future__ import annotations

from hermes.resources.scheduler.scheduler import RuntimeScheduler


class RuntimeSchedulerSelector:

    def select(
        self,
        schedulers: list[RuntimeScheduler],
    ) -> RuntimeScheduler | None:

        if not schedulers:

            return None

        return schedulers[0]
