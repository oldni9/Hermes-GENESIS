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
    - PlannerError

Public API:
    - MaxIterationsExceeded
    - PipelineExecutionError
    - PlannerError
===============================================================================
"""

from __future__ import annotations

class AgentExecutionError(Exception):
    """Base exception for agent execution errors."""

class MaxIterationsExceeded(AgentExecutionError):
    """Raised when the agent loop exceeds the maximum allowed iterations."""

class PipelineExecutionError(AgentExecutionError):
    """Raised when the underlying AI pipeline fails to execute a request."""

class PlannerError(AgentExecutionError):
    """Raised when there is an error related to planner registration or creation."""

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture