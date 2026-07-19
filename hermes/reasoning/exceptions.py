"""
===============================================================================
Reasoning Exceptions
===============================================================================
"""
from __future__ import annotations

class GraphValidationError(Exception):
    """Raised when an ExecutionGraph fails validation."""
    pass

class GraphOptimizationError(Exception):
    """Raised when graph optimization fails."""
    pass