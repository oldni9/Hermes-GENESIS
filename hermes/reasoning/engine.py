"""
===============================================================================
Hermes Reasoning Engine

Transforms Executive Decisions into
optimized Execution Graphs.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.decision import ExecutiveDecision

from hermes.reasoning.analyzer import ReasoningAnalyzer
from hermes.reasoning.executor import ReasoningExecutor
from hermes.reasoning.optimizer import ReasoningOptimizer
from hermes.reasoning.planner import ReasoningPlanner
from hermes.reasoning.validator import ReasoningValidator

from hermes.reasoning.execution_graph import ExecutionGraph


class ReasoningEngine:
    """
    Complete reasoning pipeline.

    Executive Decision
            ↓
        Analyze
            ↓
      Reasoning Context
            ↓
         Plan DAG
            ↓
        Validate
            ↓
        Optimize
            ↓
         Execute
            ↓
     Execution Graph
    """

    def __init__(self) -> None:

        self.analyzer = ReasoningAnalyzer()

        self.planner = ReasoningPlanner()

        self.validator = ReasoningValidator()

        self.optimizer = ReasoningOptimizer()

        self.executor = ReasoningExecutor()

    # ------------------------------------------------------------------

    def process(
        self,
        decision: ExecutiveDecision,
    ) -> ExecutionGraph:

        context = self.analyzer.analyze(
            decision,
        )

        graph = self.planner.build(
            context,
        )

        self.validator.validate(
            graph,
        )

        graph = self.optimizer.optimize(
            graph,
        )

        return self.executor.execute(
            graph,
        )
