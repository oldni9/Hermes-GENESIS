"""
===============================================================================
Hermes Execution Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution.context import ExecutionContext


class ExecutionValidator:
    """
    Validates execution contexts.
    """

    def validate(
        self,
        context: ExecutionContext,
    ) -> None:

        if not context.task.name:

            raise ValueError(
                "Execution task has no name."
            )