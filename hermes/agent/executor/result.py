"""
===============================================================================
Agent Executor Result
===============================================================================

Dependencies:
    - dataclasses
    - hermes.ai.response
    - hermes.agent.executor.trace

Consumes:
    - AIResponse
    - AgentTrace

Produces:
    - AgentResult

Public API:
    - AgentResult
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from hermes.ai.response import AIResponse
from hermes.agent.executor.trace import AgentTrace


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
    stop_reason: str = "completed"
    trace: Optional[AgentTrace] = None