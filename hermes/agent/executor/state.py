"""
===============================================================================
Execution State
===============================================================================

Dependencies:
    - dataclasses
    - enum
    - typing
    - uuid
    - hermes.ai.conversation
    - hermes.ai.response
    - hermes.ai.tool

Consumes:
    - AIConversation
    - AIResponse
    - ToolResult

Produces:
    - ExecutionStatus
    - ExecutionState
    - ToolFailureRecord

Public API:
    - ExecutionState

TODO:
    - Bound `planner_trace` using deque(maxlen=...) or a TraceBuffer.
    - Bound `failure_history` using deque(maxlen=20).
===============================================================================
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolResult

if TYPE_CHECKING:
    # FIX: Use TYPE_CHECKING to avoid circular import with hermes.agent.planner
    from hermes.agent.planner.telemetry import PlannerTraceEntry


class ExecutionStatus(str, Enum):
    """Status of the AgentExecutor loop."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FOR_TOOLS = "waiting_for_tools"
    FINISHED = "finished"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


@dataclass
class ToolFailureRecord:
    """A record of a failed tool execution for repeated failure detection."""
    fingerprint: str
    tool_name: str
    error: str
    iteration: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExecutionState:
    """
    Passive runtime state container for a single AgentExecutor.run() invocation.
    """
    conversation: AIConversation
    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex}")
    iteration: int = 0
    retry_count: int = 0
    status: ExecutionStatus = ExecutionStatus.IDLE
    current_response: Optional[AIResponse] = None
    response_history: List[AIResponse] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    # PR #6 Additions
    failure_history: List[ToolFailureRecord] = field(default_factory=list)
    # Type hint is evaluated as a string due to `from __future__ import annotations`
    planner_trace: List["PlannerTraceEntry"] = field(default_factory=list)