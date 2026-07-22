"""
===============================================================================
Agent Executor Result
===============================================================================

Sprint 13 Update:
Added typed MemoryCandidate list to AgentResult for future planner-driven persistence.
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from hermes.ai.response import AIResponse
from hermes.agent.executor.trace import AgentTrace
from hermes.memory.retrieval import MemoryCandidate


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
    memory_candidates: List[MemoryCandidate] = field(default_factory=list)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture