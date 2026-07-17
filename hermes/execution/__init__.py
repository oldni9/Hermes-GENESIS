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

from hermes.execution.contracts import (
    ExecutionContext,
    ExecutionEngine,
    ExecutionLifecycle,
    ExecutionRequest,
)
from hermes.execution.service import ExecutionService

__all__ = [
    "ExecutionService",
    "ExecutionContext",
    "ExecutionEngine",
    "ExecutionLifecycle",
    "ExecutionRequest",
]