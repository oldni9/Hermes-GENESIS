"""
===============================================================================
Hermes Intelligence Engine
===============================================================================
"""

from __future__ import annotations

from hermes.intelligence.analyzer import Analyzer
from hermes.intelligence.plan import ExecutionPlan
from hermes.intelligence.planner import Planner
from hermes.intelligence.request import Request


class IntelligenceEngine:

    def __init__(self) -> None:

        self._analyzer = Analyzer()

        self._planner = Planner()

    def process(
        self,
        prompt: str,
    ) -> ExecutionPlan:

        request = Request(prompt)

        intent = self._analyzer.analyze(request)

        return self._planner.create_plan(intent)