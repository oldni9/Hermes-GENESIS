"""
===============================================================================
Agent Executor Errors
===============================================================================

Dependencies:
    - None

Produces:
    - AgentExecutionError
    - MaxIterationsExceeded
    - PipelineExecutionError

Public API:
    - MaxIterationsExceeded
    - PipelineExecutionError
===============================================================================
"""

from __future__ import annotations

class AgentExecutionError(Exception):
    """Base exception for agent execution errors."""

class MaxIterationsExceeded(AgentExecutionError):
    """Raised when the agent loop exceeds the maximum allowed iterations."""

class PipelineExecutionError(AgentExecutionError):
    """Raised when the underlying AI pipeline fails to execute a request."""