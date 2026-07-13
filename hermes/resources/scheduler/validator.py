"""
===============================================================================
Hermes Runtime Scheduler Validator
===============================================================================
"""

from __future__ import annotations

from hermes.resources.scheduler.scheduler import RuntimeScheduler


class RuntimeSchedulerValidator:

    def validate(
        self,
        scheduler: RuntimeScheduler,
    ) -> None:

        if not scheduler.name.strip():

            raise ValueError(
                "Scheduler name cannot be empty."
            )