"""
===============================================================================
Hermes Agent Exceptions
===============================================================================
"""
from __future__ import annotations

class AgentError(Exception):
    """Base exception for agent-related errors."""

class AgentNotFound(AgentError):
    """Raised when an agent ID does not exist."""

class AgentMemoryError(AgentError):
    """Raised when an agent memory operation fails."""