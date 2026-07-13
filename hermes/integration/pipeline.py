"""
===============================================================================
Hermes Integration Pipeline

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.engine import ExecutiveEngine
from hermes.execution.engine import ExecutionEngine
from hermes.reasoning.engine import ReasoningEngine
from hermes.scheduler.engine import SchedulerEngine
from hermes.taskbuilder.engine import TaskBuilderEngine


class IntegrationPipeline:
    """
    Owns every subsystem required for execution.

    Runtime owns exactly one IntegrationPipeline.
    """

    def __init__(self) -> None:

        self.executive = ExecutiveEngine()

        self.reasoning = ReasoningEngine()

        self.scheduler = SchedulerEngine()

        self.taskbuilder = TaskBuilderEngine()

        self.execution = ExecutionEngine()