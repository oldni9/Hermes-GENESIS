"""
===============================================================================
Planner
===============================================================================

Dependencies:
    - typing
    - hermes.ai.response
    - hermes.agent.executor.state
    - hermes.agent.planner.decision

Consumes:
    - AIResponse
    - ExecutionState

Produces:
    - Planner
    - DefaultPlanner

Public API:
    - Planner
    - DefaultPlanner

TODO (Future PRs):
    - Implement chain-of-thought suppression
    - Implement self-reflection
    - Implement retry heuristics
    - Implement confidence estimation
===============================================================================
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from hermes.agent.executor.state import ExecutionState
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.ai.response import AIResponse


@runtime_checkable
class Planner(Protocol):
    """
    Protocol for all planners.
    """
    def decide(self, response: AIResponse, state: ExecutionState) -> PlannerDecision:
        ...


class DefaultPlanner:
    """
    The default planner acts as a pure routing mechanism based on the presence
    of tool calls and the success of the response.
    """

    def decide(self, response: AIResponse, state: ExecutionState) -> PlannerDecision:
        """Make a decision based on the current response and execution state."""
        
        # 1. Check for failure
        if not response.success:
            return PlannerDecision(
                decision=Decision.ABORT,
                reason="Response failed.",
                metadata={"error": response.message}
            )
        
        # 2. Check for tool calls
        if response.tool_calls:
            return PlannerDecision(
                decision=Decision.CALL_TOOLS,
                reason="Response contains tool calls.",
                metadata={"tool_call_count": len(response.tool_calls)}
            )
        
        # 3. Otherwise, we are done
        return PlannerDecision(
            decision=Decision.FINISH,
            reason="Final response received with no tool calls."
        )