"""
===============================================================================
Hermes Integration Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution.execution_task import ExecutionTask
from hermes.execution.result import ExecutionResult

from hermes.integration.context import IntegrationContext
from hermes.integration.pipeline import IntegrationPipeline
from hermes.integration.validator import IntegrationValidator


class IntegrationEngine:
    """
    Coordinates the complete Hermes execution pipeline.

        Prompt
            ↓
        Executive
            ↓
        Reasoning
            ↓
        Scheduler
            ↓
      Task Builder (Graph → Bundle)
            ↓
      Execution Engine
    """

    def __init__(self) -> None:

        self.pipeline = IntegrationPipeline()

        self.validator = IntegrationValidator()

    # ------------------------------------------------------------------

    def process(
        self,
        context: IntegrationContext,
    ) -> list[ExecutionResult]:

        self.validator.validate(
            context,
        )

        #
        # Executive
        #

        decision = self.pipeline.executive.process(
            context.prompt,
        )

        #
        # Reasoning
        #

        graph = self.pipeline.reasoning.process(
            decision,
        )

        #
        # Scheduler
        #

        graph = self.pipeline.scheduler.process(
            graph,
        )

        #
        # Build every KernelTask
        #

        bundle = self.pipeline.taskbuilder.process(
            graph,
        )

        #
        # Execute every KernelTask
        #

        bundle = self.pipeline.taskbuilder.process(
            graph,
        ) 

        results = self.pipeline.execution.execute(
           bundle,
        )

        return results