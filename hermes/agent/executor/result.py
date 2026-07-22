"""
===============================================================================
Agent Executor Result
===============================================================================

Dependencies:
    - dataclasses
    - enum
    - hermes.ai.response
    - hermes.agent.executor.trace

Consumes:
    - AIResponse
    - AgentTrace

Produces:
    - StopReason
    - AgentResult

Public API:
    - AgentResult
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from hermes.ai.response import AIResponse
from hermes.agent.executor.trace import AgentTrace


class StopReason(str, Enum):
    """Structured reason why the agent loop terminated."""
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    TOKEN_LIMIT = "token_limit"
    MAX_ITERATIONS = "max_iterations"
    MAX_REFLECTIONS = "max_reflections"
    PIPELINE_ERROR = "pipeline_error"


@dataclass(frozen=True)
class AgentResult:
    """
    Immutable result object returned by the AgentExecutor.
    Contains the final LLM response and execution metrics.
    """
    response: AIResponse
    iterations: int
    duration: float
    token_usage: Optional[dict] = None
    stop_reason: StopReason = StopReason.COMPLETED
    trace: Optional[AgentTrace] = None

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture