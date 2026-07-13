"""
===============================================================================
Hermes Agent Exceptions
===============================================================================
"""

from __future__ import annotations


class AgentError(Exception):
    """
    Base Agent Exception.
    """


class AgentAlreadyExists(AgentError):
    """
    Agent already exists.
    """


class AgentNotFound(AgentError):
    """
    Agent not found.
    """


class AgentValidationError(AgentError):
    """
    Invalid Runtime Agent.
    """