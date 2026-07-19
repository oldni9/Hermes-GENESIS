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
    - hermes.agent.planner.telemetry
    - hermes.agent.planner.tool_validation

Consumes:
    - AIResponse
    - ExecutionState
    - ConfidenceEvaluator
    - List[PlannerRule]
    - PlannerPolicy
    - ToolRegistry

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
from hermes.agent.planner.telemetry import PlannerTraceEntry
from hermes.agent.planner.tool_validation import ToolValidator
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolRegistry


class ReasoningPlanner:
    """
    A rule-based planner that evaluates responses against a set of heuristics
    before deciding the next action. Records telemetry traces for observability.
    """
    def __init__(
        self,
        policy: Optional[PlannerPolicy] = None,
        confidence_evaluator: Optional[ConfidenceEvaluator] = None,
        rules: Optional[List[PlannerRule]] = None,
        registry: Optional[ToolRegistry] = None
    ):
        self._policy = policy or PlannerPolicy()
        self._confidence_evaluator = confidence_evaluator or HeuristicConfidenceEvaluator()
        
        tool_validator = ToolValidator(registry) if registry else None
        
        self._rules = rules or DefaultPlannerRules(self._confidence_evaluator, tool_validator)

    def decide(self, response: AIResponse, state: ExecutionState) -> PlannerDecision:
        """
        Evaluates the response against all rules in order.
        Records telemetry for every rule evaluated.
        """
        for rule in self._rules:
            decision = rule.evaluate(response, state, self._policy)
            rule_name = rule.__class__.__name__
            matched = decision is not None
            
            # Record telemetry
            state.planner_trace.append(PlannerTraceEntry(
                iteration=state.iteration,
                rule_name=rule_name,
                matched=matched,
                decision=decision.decision if decision else None,
                reason=decision.reason if decision else ""
            ))
            
            if decision is not None:
                return decision
                
        return PlannerDecision(
            decision=Decision.ABORT,
            reason="No planner rule matched the current state."
        )