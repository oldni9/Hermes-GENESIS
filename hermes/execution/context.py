"""
===============================================================================
Hermes Execution Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations
"""
===============================================================================
Hermes Execution Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""
from __future__ import annotations

from hermes.execution.contracts import ExecutionContext


class ExecutionValidator:
    """
    Validates execution contexts.
    """

    def validate(
        self,
        context: ExecutionContext,
    ) -> None:

        if not context.request_id:
            raise ValueError("Execution context must have a request_id.")
from dataclasses import dataclass

from hermes.execution.execution_task import ExecutionTask


@dataclass(slots=True)
class ExecutionContext:
    """
    Runtime execution context.
    """

    task: ExecutionTask
