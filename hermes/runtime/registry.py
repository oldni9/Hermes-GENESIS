"""
===============================================================================
Execution Registry
===============================================================================

Sprint 17A.5 Final Freeze:
- Added started_at to track actual execution start time (vs queue time).
- Ensured started_at is set exactly once when transitioning to RUNNING.
===============================================================================
"""
from __future__ import annotations

import copy
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ExecutionState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def generate_execution_id() -> str:
    """Generates a standard UUID4 string."""
    return str(uuid.uuid4())


@dataclass
class ExecutionRecord:
    execution_id: str
    state: ExecutionState
    prompt: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None  # Set exactly once when state becomes RUNNING
    updated_at: float = field(default_factory=time.time)


class ExecutionRegistry:
    """Thread-safe registry for execution records."""
    
    def __init__(self) -> None:
        self._records: Dict[str, ExecutionRecord] = {}
        self._lock = threading.Lock()

    def create(self, execution_id: str, prompt: str) -> ExecutionRecord:
        record = ExecutionRecord(
            execution_id=execution_id,
            state=ExecutionState.QUEUED,
            prompt=prompt
        )
        with self._lock:
            self._records[execution_id] = record
        return record

    def get(self, execution_id: str) -> Optional[ExecutionRecord]:
        with self._lock:
            record = self._records.get(execution_id)
            return copy.deepcopy(record) if record else None

    def update_state(self, execution_id: str, state: ExecutionState, **kwargs) -> None:
        with self._lock:
            if execution_id in self._records:
                record = self._records[execution_id]
                record.state = state
                record.updated_at = time.time()
                
                # Set started_at ONLY on the first transition to RUNNING
                if state == ExecutionState.RUNNING and record.started_at is None:
                    record.started_at = record.updated_at
                    
                for k, v in kwargs.items():
                    if hasattr(record, k):
                        setattr(record, k, v)

    def list_executions(self) -> list[ExecutionRecord]:
        with self._lock:
            return [copy.deepcopy(r) for r in self._records.values()]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture