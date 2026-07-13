"""
===============================================================================
Hermes Execution Queue

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import deque

from hermes.execution.execution_task import ExecutionTask


class ExecutionQueue:

    def __init__(self) -> None:

        self._queue = deque()

    # ------------------------------------------------------------------

    def push(
        self,
        task: ExecutionTask,
    ) -> None:

        self._queue.append(task)

    # ------------------------------------------------------------------

    def pop(
        self,
    ) -> ExecutionTask:

        return self._queue.popleft()

    # ------------------------------------------------------------------

    def empty(
        self,
    ) -> bool:

        return not self._queue