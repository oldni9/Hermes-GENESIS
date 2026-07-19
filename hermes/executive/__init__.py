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
    ExecutionEngine,      # Protocol
    ExecutionLifecycle,
    ExecutionRequest,
)
from hermes.execution.service import ExecutionService

__all__ = [
    "ExecutionService",
    "ExecutionContext",
    "ExecutionLifecycle",
    "ExecutionRequest",
    "ExecutionEngine",    # Protocol from contracts.py
]

# Note: The concrete ExecutionEngine class (from engine.py) is not exported here
# to avoid conflict with the protocol. Import it directly from hermes.execution.engine
# if needed.