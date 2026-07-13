"""
===============================================================================
Hermes Executive Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.context import ExecutiveContext


class ExecutiveValidator:

    def validate(
        self,
        context: ExecutiveContext,
    ) -> None:

        if not context.prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )