"""
===============================================================================
Hermes Task Builder Engine

Converts an ExecutionGraph into a KernelTaskBundle.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel.kernel_task_bundle import KernelTaskBundle

from hermes.reasoning.execution_graph import ExecutionGraph

from hermes.taskbuilder.builder import TaskBuilder
from hermes.taskbuilder.mapper import TaskBuilderMapper
from hermes.taskbuilder.validator import TaskBuilderValidator


class TaskBuilderEngine:
    """
    Converts an ExecutionGraph into executable KernelTasks.

        ExecutionGraph
             ↓
      Iterate Nodes
             ↓
           Mapper
             ↓
          Context
             ↓
         Validation
             ↓
        Task Builder
             ↓
      KernelTaskBundle
    """

    def __init__(self) -> None:

        self.mapper = TaskBuilderMapper()

        self.validator = TaskBuilderValidator()

        self.builder = TaskBuilder()

    # ------------------------------------------------------------------

    def process(
        self,
        graph: ExecutionGraph,
    ) -> KernelTaskBundle:
        """
        Build KernelTasks for every node
        inside the ExecutionGraph.
        """

        bundle = KernelTaskBundle()

        for node in graph.all_nodes():

            context = self.mapper.map(
                node,
            )

            self.validator.validate(
                context,
            )

            task = self.builder.build(
                context,
            )

            bundle.add(
                task,
            )

        return bundle