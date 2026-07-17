"""
===============================================================================
Hermes AI Orchestrator Exceptions

Orchestrator-specific exceptions.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class OrchestratorError(Exception):
    """Base orchestrator exception."""
    pass


class ValidationError(OrchestratorError):
    """Request validation failed."""
    pass


class ProviderSelectionError(OrchestratorError):
    """Provider selection failed."""
    pass


class ExecutionError(OrchestratorError):
    """Provider execution failed."""
    pass


class RetryExhaustedError(ExecutionError):
    """All retry attempts exhausted."""
    pass