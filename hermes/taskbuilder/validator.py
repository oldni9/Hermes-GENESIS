"""
===============================================================================
Hermes Task Builder Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.taskbuilder.context import TaskBuilderContext


class TaskBuilderValidator:
    """
    Validates TaskBuilderContext.
    """

    def validate(
        self,
        context: TaskBuilderContext,
    ) -> None:

        if not context.name:

            raise ValueError(
                "Task has no name."
            )