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
    - hermes.agent.planner.hasher
    - hermes.agent.planner.tool_validation

Consumes:
    - AIResponse
    - ExecutionState
    - PlannerPolicy
    - ConfidenceEvaluator
    - ToolValidator

Produces:
    - PlannerRule
    - ToolAvailabilityRule
    - RepeatedToolFailureRule
    - EmptyResponseRule
    - WeakAnswerRule
    - ToolCallRule
    - FinishRule

Public API:
    - PlannerRule
    - DefaultPlannerRules
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from hermes.agent.executor.state import ExecutionState
from hermes.agent.planner.confidence import ConfidenceEvaluator
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.planner.hasher import ToolCallHasher
from hermes.agent.planner.policy import PlannerPolicy
from hermes.agent.planner.tool_validation import ToolValidationStatus, ToolValidator
from hermes.ai.response import AIResponse


class PlannerRule(ABC):
    @abstractmethod
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        ...


class ToolAvailabilityRule(PlannerRule):
    """Validates tool availability before allowing execution."""
    
    def __init__(self, validator: ToolValidator):
        self._validator = validator

    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not response.tool_calls:
            return None

        results = self._validator.validate_batch(response.tool_calls)
        
        for res in results:
            if res.status != ToolValidationStatus.VALID:
                if res.status in [ToolValidationStatus.UNKNOWN_TOOL, ToolValidationStatus.DISABLED_TOOL]:
                    return PlannerDecision(
                        decision=Decision.ABORT,
                        reason=res.reason,
                        metadata={"validation_status": res.status.value}
                    )
                else:
                    return PlannerDecision(
                        decision=Decision.RETRY,
                        reason=res.reason,
                        feedback=f"Tool call to '{res.tool_call.function.name}' failed validation: {res.reason}. Please check arguments."
                    )
        return None


class RepeatedToolFailureRule(PlannerRule):
    """Detects if the LLM is trying to call a tool that just failed with the same arguments."""
    
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.abort_on_repeated_failure or not response.tool_calls or not state.failure_history:
            return None

        failed_fingerprints = {rec.fingerprint for rec in state.failure_history}

        for tc in response.tool_calls:
            fingerprint = ToolCallHasher.fingerprint(tc)
            if fingerprint in failed_fingerprints:
                return PlannerDecision(
                    decision=Decision.ABORT,
                    reason=f"Repeated failure detected for tool '{tc.function.name}' with identical arguments.",
                    metadata={"fingerprint": fingerprint}
                )
        return None


class EmptyResponseRule(PlannerRule):
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.retry_on_empty or not response.success or response.tool_calls:
            return None
            
        text = response.text().strip()
        if not text:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(decision=Decision.ABORT, reason="Empty response received and retry limit reached.")
            return PlannerDecision(
                decision=Decision.RETRY,
                reason="Empty response received.",
                feedback="Your previous response was empty. Please provide a complete response or use a tool."
            )
        return None


class WeakAnswerRule(PlannerRule):
    def __init__(self, confidence_evaluator: ConfidenceEvaluator):
        self._evaluator = confidence_evaluator

    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if not policy.retry_on_low_confidence or not response.success or response.tool_calls:
            return None
            
        text = response.text().strip()
        
        if len(text) < policy.minimum_response_length:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(decision=Decision.ABORT, reason="Weak answer received and retry limit reached.")
            return PlannerDecision(
                decision=Decision.RETRY,
                reason=f"Response too short (len={len(text)}).",
                feedback=f"Your previous response was too short (len={len(text)}). Please elaborate or use a tool."
            )
            
        confidence = self._evaluator.evaluate(response, state)
        if confidence < policy.min_confidence_threshold:
            if state.retry_count >= policy.max_retries_on_failure:
                return PlannerDecision(decision=Decision.ABORT, reason="Low confidence answer received and retry limit reached.")
            return PlannerDecision(
                decision=Decision.RETRY,
                reason=f"Low confidence score ({confidence}).",
                metadata={"confidence": confidence},
                feedback=f"Your previous response had low confidence ({confidence}). Please try again or use a tool."
            )
            
        return None


class ToolCallRule(PlannerRule):
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if response.success and response.tool_calls:
            return PlannerDecision(
                decision=Decision.CALL_TOOLS,
                reason="Response contains tool calls.",
                metadata={"tool_call_count": len(response.tool_calls)}
            )
        return None


class FinishRule(PlannerRule):
    def evaluate(self, response: AIResponse, state: ExecutionState, policy: PlannerPolicy) -> Optional[PlannerDecision]:
        if response.success and not response.tool_calls:
            return PlannerDecision(decision=Decision.FINISH, reason="Final response received with no tool calls.")
        return None


def DefaultPlannerRules(confidence_evaluator: ConfidenceEvaluator, tool_validator: Optional[ToolValidator] = None) -> List[PlannerRule]:
    """Returns the default set of rules in priority order."""
    rules: List[PlannerRule] = []
    
    if tool_validator:
        rules.append(ToolAvailabilityRule(tool_validator))
        
    rules.extend([
        RepeatedToolFailureRule(),
        EmptyResponseRule(),
        WeakAnswerRule(confidence_evaluator),
        ToolCallRule(),
        FinishRule(),
    ])
    
    return rules