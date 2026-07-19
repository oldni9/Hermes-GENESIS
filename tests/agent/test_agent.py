"""
===============================================================================
Tests for Agent
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.agent.agent import Agent
from hermes.agent.memory import AgentMemory
from hermes.ai.tool import Tool


def test_agent_initialization():
    agent = Agent(agent_id="test-id", system_prompt="You are a test agent.")
    assert agent.id == "test-id"
    assert agent.system_prompt == "You are a test agent."
    assert agent.tools == []
    assert isinstance(agent.memory, AgentMemory)
    assert agent.session is not None


def test_agent_with_tools():
    tool = Tool(name="test_tool", description="A test tool")
    agent = Agent(agent_id="test-id", system_prompt="test", tools=[tool])
    assert agent.tools == [tool]


def test_agent_with_memory():
    memory = AgentMemory()
    agent = Agent(agent_id="test-id", system_prompt="test", memory=memory)
    assert agent.memory is memory