"""
===============================================================================
Planner Telemetry
===============================================================================

Dependencies:
    - dataclasses
    - time
    - hermes.agent.planner.decision

Consumes:
    - Decision

Produces:
    - PlannerTraceEntry

Public API:
    - PlannerTraceEntry
===============================================================================
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from hermes.agent.planner.decision import Decision


@dataclass
class PlannerTraceEntry:
    """
    A single entry in the planner's execution trace.
    """
    iteration: int
    rule_name: str
    matched: bool
    decision: Optional[Decision]
    reason: str
    timestamp: float = field(default_factory=time.time)