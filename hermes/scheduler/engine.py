"""
===============================================================================
Hermes Scheduler Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""
from __future__ import annotations

from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.scheduler.context import SchedulerContext
from hermes.scheduler.executor import SchedulerExecutor
from hermes.scheduler.queue import SchedulerQueue
from hermes.scheduler.selector import SchedulerSelector
from hermes.scheduler.validator import SchedulerValidator


class SchedulerEngine:
    """
    Executes an Execution Graph.

    Pipeline

        Graph
          ↓
      Context
          ↓
      Validation
          ↓
      Select Nodes
          ↓
      Queue
          ↓
      Execute
    """

    def __init__(self) -> None:
        self.validator = SchedulerValidator()
        self.selector = SchedulerSelector()
        self.queue = SchedulerQueue()
        self.executor = SchedulerExecutor()

    # ------------------------------------------------------------------

    def process(
        self,
        graph: ExecutionGraph,
    ) -> ExecutionGraph:
        """
        Process an ExecutionGraph.
        """
        context = SchedulerContext(
            graph=graph,
        )

        self.validator.validate(
            context,
        )

        for node in self.selector.select(graph):
            self.queue.push(node)

        while not self.queue.empty():
            node = self.queue.pop()
            self.executor.execute(node)

        return graph