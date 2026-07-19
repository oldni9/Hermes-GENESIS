"""
===============================================================================
Hermes Execution Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution.result import ExecutionResult


class ExecutionRegistry:
    """
    Stores execution results.
    """

    def __init__(self) -> None:

        self._results: list[ExecutionResult] = []

    # ------------------------------------------------------------------

    def add(
        self,
        result: ExecutionResult,
    ) -> None:

        self._results.append(result)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[ExecutionResult]:

        return list(self._results)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._results.clear()
