"""
===============================================================================
Hermes Scheduler Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.scheduler.context import SchedulerContext


class SchedulerValidator:
    """
    Validates scheduler context.
    """

    def validate(
        self,
        context: SchedulerContext,
    ) -> None:

        if not context.graph.nodes:

            raise ValueError("Execution graph is empty.")
