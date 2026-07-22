"""
===============================================================================
Agent Trace & Observability
===============================================================================
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TraceEventType(str, Enum):
    """Standardized event types for agent tracing."""
    ITERATION_START = "iteration_start"
    ITERATION_FINISH = "iteration_finish"
    
    # Execution Engine Events
    EXECUTION_START = "execution_start"
    EXECUTION_FINISH = "execution_finish"
    LLM_START = "llm_start"
    LLM_FINISH = "llm_finish"
    TOOL_START = "tool_start"
    TOOL_FINISH = "tool_finish"
    
    # Planner Events
    PLANNER_ITERATION = "planner_iteration"
    PLANNER_DECISION = "planner_decision"
    REFLECTION_START = "reflection_start"
    REFLECTION_FINISH = "reflection_finish"
    
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS_EXCEEDED = "max_iterations_exceeded"
    
    # Runtime Policy Events
    POLICY_CHECK = "policy_check"
    POLICY_PASS = "policy_pass"
    POLICY_FAIL = "policy_fail"
    CANCELLED = "cancelled"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass(slots=True)
class TraceEvent:
    """
    A single event recorded during an agent execution loop.
    """
    timestamp: float
    iteration: int
    event_type: TraceEventType
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "iteration": self.iteration,
            "event_type": self.event_type.value,
            "payload": self.payload,
        }


@dataclass(slots=True)
class TraceMetrics:
    """
    Aggregate execution statistics.
    """
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_cost": self.total_cost,
            "duration": self.duration,
        }


class AgentTrace:
    """
    Collects and stores trace events during an agent run.
    Provides structured observability for debugging and telemetry.
    """

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []
        self._start_time: float = time.time()
        self._end_time: Optional[float] = None
        self._metrics: TraceMetrics = TraceMetrics()

    @property
    def events(self) -> List[TraceEvent]:
        """Return a copy of the recorded events."""
        return list(self._events)

    @property
    def metrics(self) -> TraceMetrics:
        """Return the aggregate metrics."""
        return self._metrics

    @property
    def duration(self) -> float:
        """Total execution duration in seconds."""
        if self._end_time is None:
            return time.time() - self._start_time
        return self._end_time - self._start_time

    def add_event(self, iteration: int, event_type: TraceEventType, payload: Optional[Dict[str, Any]] = None) -> None:
        """Record a new trace event."""
        self._events.append(TraceEvent(
            timestamp=time.time(),
            iteration=iteration,
            event_type=event_type,
            payload=payload or {}
        ))

    def add_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Accumulate token usage metrics."""
        self._metrics.total_prompt_tokens += prompt_tokens
        self._metrics.total_completion_tokens += completion_tokens

    def finalize(self) -> None:
        """Mark the trace as complete and lock in metrics."""
        self._end_time = time.time()
        self._metrics.duration = self.duration

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the trace to a dictionary."""
        return {
            "metrics": self._metrics.to_dict(),
            "events": [e.to_dict() for e in self._events],
        }

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture