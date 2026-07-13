"""
===============================================================================
Hermes Execution Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.execution.execution_task import ExecutionTask


@dataclass(slots=True)
class ExecutionContext:
    """
    Runtime execution context.
    """

    task: ExecutionTask