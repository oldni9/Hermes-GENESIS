"""
===============================================================================
Tests for Agent Exceptions
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.agent.exceptions import AgentError, AgentNotFound, AgentMemoryError


def test_agent_error():
    with pytest.raises(AgentError):
        raise AgentError("test")


def test_agent_not_found():
    with pytest.raises(AgentNotFound):
        raise AgentNotFound("agent not found")


def test_agent_memory_error():
    with pytest.raises(AgentMemoryError):
        raise AgentMemoryError("memory error")