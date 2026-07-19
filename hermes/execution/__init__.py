"""
===============================================================================
Hermes Execution Package

Coordinates execution of AI requests.

This package contains the execution service and execution contracts.

Exports:
    - ExecutionService
    - ExecutionContracts (via .contracts)
===============================================================================
"""
from __future__ import annotations

from hermes.execution.contracts import (
    ExecutionContext,
    ExecutionLifecycle,
    ExecutionRequest,
)
from hermes.execution.service import ExecutionService
from hermes.execution.engine import ExecutionEngine

__all__ = [
    "ExecutionService",
    "ExecutionContext",
    "ExecutionLifecycle",
    "ExecutionRequest",
    "ExecutionEngine",
]