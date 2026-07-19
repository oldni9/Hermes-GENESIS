"""
===============================================================================
Planner Heuristics / Rules
===============================================================================

Dependencies:
    - abc
    - typing
    - hermes.ai.response
    - hermes.agent.executor.state
    - hermes.agent.planner.decision
    - hermes.agent.planner.policy
    - hermes.agent.planner.confidence

Consumes:
    - AIResponse
    - ExecutionState
    - PlannerPolicy
    - ConfidenceEvaluator

Produces:
    - PlannerRule
    - RepeatedToolFailureRule
    - EmptyResponseRule
    - WeakAnswerRule
    - ToolCallRule
    - FinishRule

Public API:
    - PlannerRule
    - DefaultPlannerRules

Rule Ordering:
1. EmptyResponseRule
2. WeakAnswerRule
3. ToolCallRule
4. FinishRule
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from hermes.agent.executor.state import ExecutionState
from hermes.agent.planner.confidence import ConfidenceEvaluator
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.planner.policy import PlannerPolicy
from hermes.ai.response import AIResponse


class PlannerRule(ABC):
    """
    Abstract base class for all planner rules.
    """
    @abstractmethod
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        ...


class RepeatedToolFailureRule(PlannerRule):
    """
    Detects if the LLM is trying to call a tool that just failed.
    NOTE: Reserved for PR #6 once argument hashing exists. Not included in DefaultPlannerRules.
    """
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.abort_on_repeated_failure or not response.tool_calls or not state.tool_results:
            return None

        last_result = state.tool_results[-1]
        if not last_result.failed:
            return None

        # TODO: Compare normalized arguments hash to prevent false positives.
        for tc in response.tool_calls:
            if tc.id == last_result.call_id:
                return PlannerDecision(
                    decision=Decision.ABORT,
                    reason=f"Repeated failure detected for tool call ID '{last_result.call_id}'.",
                    metadata={"call_id": last_result.call_id, "error": last_result.error}
                )
        return None


class EmptyResponseRule(PlannerRule):
    """
    Detects empty responses and retries if configured and retry limit not reached.
    """
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.retry_on_empty or not response.success or response.tool_calls:
            return None
            
        text = response.text().strip()
        if not text:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(
                    decision=Decision.ABORT,
                    reason="Empty response received and retry limit reached."
                )
            return PlannerDecision(
                decision=Decision.RETRY,
                reason="Empty response received.",
                feedback="Your previous response was empty. Please provide a complete response or use a tool."
            )
        return None


class WeakAnswerRule(PlannerRule):
    """
    Evaluates confidence and retries if the answer is too weak and retry limit not reached.
    """
    def __init__(self, confidence_evaluator: ConfidenceEvaluator):
        self._evaluator = confidence_evaluator

    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.retry_on_low_confidence or not response.success or response.tool_calls:
            return None
            
        text = response.text().strip()
        
        if len(text) < policy.minimum_response_length:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(
                    decision=Decision.ABORT,
                    reason="Weak answer received and retry limit reached."
                )
            return PlannerDecision(
                decision=Decision.RETRY,
                reason=f"Response too short (len={len(text)}).",
                feedback=f"Your previous response was too short (len={len(text)}). Please elaborate or use a tool."
            )
            
        confidence = self._evaluator.evaluate(response, state)
        if confidence < policy.min_confidence_threshold:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(
                    decision=Decision.ABORT,
                    reason="Low confidence answer received and retry limit reached."
                )
            return PlannerDecision(
                decision=Decision.RETRY,
                reason=f"Low confidence score ({confidence}).",
                metadata={"confidence": confidence},
                feedback=f"Your previous response had low confidence ({confidence}). Please try again or use a tool."
            )
            
        return None


class ToolCallRule(PlannerRule):
    """
    If tool calls are present and no previous rule aborted, execute them.
    """
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if response.success and response.tool_calls:
            return PlannerDecision(
                decision=Decision.CALL_TOOLS,
                reason="Response contains tool calls.",
                metadata={"tool_call_count": len(response.tool_calls)}
            )
        return None


class FinishRule(PlannerRule):
    """
    If no other rule matched and the response is successful, finish.
    """
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if response.success and not response.tool_calls:
            return PlannerDecision(
                decision=Decision.FINISH,
                reason="Final response received with no tool calls."
            )
        return None


def DefaultPlannerRules(confidence_evaluator: ConfidenceEvaluator) -> List[PlannerRule]:
    """
    Returns the default set of rules in priority order.
    """
    return [
        EmptyResponseRule(),
        WeakAnswerRule(confidence_evaluator),
        ToolCallRule(),
        FinishRule(),
    ]