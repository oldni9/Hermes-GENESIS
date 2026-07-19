"""
===============================================================================
Execution Context
===============================================================================

Dependencies:
    - dataclasses
    - time
    - uuid
    - typing

Consumes:
    - None

Produces:
    - ExecutionContext

Public API:
    - ExecutionContext
===============================================================================
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ExecutionContext:
    """
    Lightweight, immutable context for a single agent execution run.
    """
    execution_id: str
    workspace_id: str
    start_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Placeholder for future cooperative cancellation token
    cancellation_token: Optional[Any] = None

    @staticmethod
    def create(workspace_id: str, metadata: Optional[Dict[str, Any]] = None) -> "ExecutionContext":
        """Factory method to create a new ExecutionContext with a generated ID."""
        execution_id = f"exec_{uuid.uuid4().hex}"
        return ExecutionContext(
            execution_id=execution_id,
            workspace_id=workspace_id,
            metadata=metadata or {}
        )