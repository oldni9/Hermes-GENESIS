"""
===============================================================================
Confidence Evaluator
===============================================================================

Dependencies:
    - typing
    - hermes.ai.response
    - hermes.agent.executor.state

Consumes:
    - AIResponse
    - ExecutionState

Produces:
    - ConfidenceEvaluator
    - HeuristicConfidenceEvaluator

Public API:
    - ConfidenceEvaluator
    - HeuristicConfidenceEvaluator

TODO (Future PRs):
    - Implement LLMConfidenceEvaluator
    - Implement RewardModelConfidenceEvaluator
===============================================================================
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from hermes.agent.executor.state import ExecutionState
from hermes.ai.response import AIResponse

# FIX: Constants instead of magic numbers
LOW_CONFIDENCE = 0.25
HIGH_CONFIDENCE = 1.0


class ConfidenceEvaluator(Protocol):
    """
    Protocol for evaluating the confidence of an LLM response.
    
    Contract:
    - 0.0 indicates impossible / no confidence.
    - 1.0 indicates absolute certainty.
    """
    def evaluate(self, response: AIResponse, state: ExecutionState) -> float:
        ...


class HeuristicConfidenceEvaluator:
    """
    A simple heuristic evaluator that checks for low-confidence markers.
    Returns a float between 0.0 and 1.0.
    """
    LOW_CONFIDENCE_MARKERS = ["i don't know", "i'm not sure", "i cannot", "i can't"]

    def evaluate(self, response: AIResponse, state: ExecutionState) -> float:
        text = response.text().lower()
        for marker in self.LOW_CONFIDENCE_MARKERS:
            if marker in text:
                return LOW_CONFIDENCE
        return HIGH_CONFIDENCE