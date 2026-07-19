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

Public API:
    - ExecutionState

TODO:
    - Add tracing and telemetry spans to the state.
    - Add cooperative cancellation token.
===============================================================================
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolResult


class ExecutionStatus(str, Enum):
    """Status of the AgentExecutor loop."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FOR_TOOLS = "waiting_for_tools"
    FINISHED = "finished"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


@dataclass
class ExecutionState:
    """
    Passive runtime state container for a single AgentExecutor.run() invocation.
    """
    conversation: AIConversation
    execution_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    iteration: int = 0
    retry_count: int = 0  # FIX: Added retry_count to enforce max_retries_on_failure
    status: ExecutionStatus = ExecutionStatus.IDLE
    current_response: Optional[AIResponse] = None
    response_history: List[AIResponse] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)