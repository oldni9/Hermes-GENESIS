"""
===============================================================================
Hermes Agent Response
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from hermes.planning.plan import Plan
from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.agent.session import AgentSession


@dataclass(slots=True)
class AgentResponse:
    """
    Result of an agent execution.
    Contains success status, the main text output, and optional introspection.
    """
    success: bool
    text: str
    data: Any = None
    session: Optional[AgentSession] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Optional introspection fields (may be None)
    plan: Optional[Plan] = None
    execution_graph: Optional[ExecutionGraph] = None