"""
===============================================================================
Hermes Scheduler Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.reasoning.execution_graph import ExecutionGraph


@dataclass(slots=True)
class SchedulerContext:
    """
    Runtime scheduler context.
    """

    graph: ExecutionGraph

    metadata: dict[str, Any] = field(default_factory=dict)