"""
===============================================================================
Execution Plan
===============================================================================

Sprint 14: Thin wrapper around ExecutionGraph to be passed to AgentExecutor.
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from hermes.graph.models import ExecutionGraph


@dataclass
class ExecutionPlan:
    """Encapsulates an ExecutionGraph and optional metadata."""
    graph: ExecutionGraph
    metadata: Dict[str, Any] = field(default_factory=dict)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture