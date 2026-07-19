"""
===============================================================================
Reasoning Planner
===============================================================================

Dependencies:
    - typing
    - hermes.ai.response
    - hermes.agent.executor.state
    - hermes.agent.planner.confidence
    - hermes.agent.planner.decision
    - hermes.agent.planner.heuristics
    - hermes.agent.planner.policy

Consumes:
    - AIResponse
    - ExecutionState
    - ConfidenceEvaluator
    - List[PlannerRule]
    - PlannerPolicy

Produces:
    - ReasoningPlanner

Public API:
    - ReasoningPlanner
===============================================================================
"""

from __future__ import annotations

from typing import List, Optional

from hermes.agent.executor.state import ExecutionState
from hermes.agent.planner.confidence import ConfidenceEvaluator, HeuristicConfidenceEvaluator
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.planner.heuristics import DefaultPlannerRules, PlannerRule
from hermes.agent.planner.policy import PlannerPolicy
from hermes.ai.response import AIResponse


class ReasoningPlanner:
    """
    A rule-based planner that evaluates responses against a set of heuristics
    before deciding the next action.
    """
    def __init__(
        self,
        policy: Optional[PlannerPolicy] = None,
        confidence_evaluator: Optional[ConfidenceEvaluator] = None,
        rules: Optional[List[PlannerRule]] = None
    ):
        self._policy = policy or PlannerPolicy()
        self._confidence_evaluator = confidence_evaluator or HeuristicConfidenceEvaluator()
        self._rules = rules or DefaultPlannerRules(self._confidence_evaluator)

    def decide(self, response: AIResponse, state: ExecutionState) -> PlannerDecision:
        """
        Evaluates the response against all rules in order.
        The first rule that returns a decision wins.
        """
        for rule in self._rules:
            decision = rule.evaluate(response, state, self._policy)
            if decision is not None:
                return decision
                
        return PlannerDecision(
            decision=Decision.ABORT,
            reason="No planner rule matched the current state."
        )