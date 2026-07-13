"""
===============================================================================
Hermes Execution State

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class ExecutionState(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"