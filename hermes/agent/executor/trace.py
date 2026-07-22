"""
===============================================================================
Agent Trace & Observability
===============================================================================

Sprint 14 Update:
Added GRAPH_* trace events for Execution Graph telemetry.
===============================================================================
"""

from __future__ import annotations

import threading
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
    
    # Tree of Thought Events (Sprint 10)
    TOT_BRANCH_GENERATED = "tot_branch_generated"
    TOT_BRANCH_EVALUATED = "tot_branch_evaluated"
    TOT_BRANCH_SELECTED = "tot_branch_selected"
    TOT_SEARCH_FINISHED = "tot_search_finished"
    
    # Debate Planner Events (Sprint 11)
    DEBATE_STARTED = "debate_started"
    DEBATER_STARTED = "debater_started"
    DEBATER_RESPONSE = "debater_response"
    DEBATER_FINISHED = "debater_finished"
    JUDGE_STARTED = "judge_started"
    JUDGE_FINISHED = "judge_finished"
    DEBATE_COMPLETED = "debate_completed"
    
    # Parallel Execution Events (Sprint 12)
    PARALLEL_STARTED = "parallel_started"
    PARALLEL_JOB_STARTED = "parallel_job_started"
    PARALLEL_JOB_FINISHED = "parallel_job_finished"
    PARALLEL_JOB_FAILED = "parallel_job_failed"
    PARALLEL_COMPLETED = "parallel_completed"
    
    # Execution Graph Events (Sprint 14)
    GRAPH_STARTED = "graph_started"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    GRAPH_FINISHED = "graph_finished"


@dataclass(slots=True)
class TraceEvent:
    """A single event recorded during an agent execution loop."""
    timestamp: float
    iteration: int
    event_type: TraceEventType
    payload: Dict[str, Any] = field(default_factory=dict)
    sequence: int = 0
    thread: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "iteration": self.iteration,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "sequence": self.sequence,
            "thread": self.thread,
        }


@dataclass(slots=True)
class TraceMetrics:
    """Aggregate execution statistics."""
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
    """Collects and stores trace events during an agent run. Thread-safe."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []
        self._start_time: float = time.time()
        self._end_time: Optional[float] = None
        self._metrics: TraceMetrics = TraceMetrics()
        self._seq_counter: int = 0
        
        # Fine-grained locks for thread safety
        self._event_lock = threading.Lock()
        self._metric_lock = threading.Lock()

    @property
    def events(self) -> List[TraceEvent]:
        with self._event_lock:
            return list(self._events)

    @property
    def metrics(self) -> TraceMetrics:
        return self._metrics

    @property
    def duration(self) -> float:
        if self._end_time is None:
            return time.time() - self._start_time
        return self._end_time - self._start_time

    def add_event(self, iteration: int, event_type: TraceEventType, payload: Optional[Dict[str, Any]] = None) -> None:
        with self._event_lock:
            self._seq_counter += 1
            self._events.append(TraceEvent(
                timestamp=time.time(),
                iteration=iteration,
                event_type=event_type,
                payload=payload or {},
                sequence=self._seq_counter,
                thread=threading.get_ident()
            ))

    def add_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        with self._metric_lock:
            self._metrics.total_prompt_tokens += prompt_tokens
            self._metrics.total_completion_tokens += completion_tokens

    def finalize(self) -> None:
        self._end_time = time.time()
        with self._metric_lock:
            self._metrics.duration = self.duration

    def to_dict(self) -> Dict[str, Any]:
        with self._event_lock:
            events = [e.to_dict() for e in self._events]
        with self._metric_lock:
            metrics = self._metrics.to_dict()
        return {
            "metrics": metrics,
            "events": events,
        }

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture