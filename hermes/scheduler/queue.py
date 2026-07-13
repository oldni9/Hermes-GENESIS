"""
===============================================================================
Hermes Scheduler Queue

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import deque

from hermes.reasoning.execution_node import ExecutionNode


class SchedulerQueue:

    def __init__(self) -> None:

        self._queue = deque()

    # ------------------------------------------------------------------

    def push(
        self,
        node: ExecutionNode,
    ) -> None:

        self._queue.append(node)

    # ------------------------------------------------------------------

    def pop(
        self,
    ) -> ExecutionNode:

        return self._queue.popleft()

    # ------------------------------------------------------------------

    def empty(
        self,
    ) -> bool:

        return not self._queue