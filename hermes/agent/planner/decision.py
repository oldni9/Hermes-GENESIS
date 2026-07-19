"""
===============================================================================
Planner Decision
===============================================================================

Dependencies:
    - enum
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - Decision
    - PlannerDecision

Public API:
    - Decision
    - PlannerDecision
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Decision(str, Enum):
    """Decisions the planner can make."""
    CONTINUE = "continue"
    CALL_TOOLS = "call_tools"
    FINISH = "finish"
    RETRY = "retry"
    ABORT = "abort"


@dataclass
class PlannerDecision:
    """
    The result of a planner's decision.
    """
    decision: Decision
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    feedback: Optional[str] = None  # Used for RETRY decisions to guide the LLM