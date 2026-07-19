"""
===============================================================================
Tests for Agent Context Factory
===============================================================================
"""

import pytest
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolContext


@pytest.fixture
def factory():
    return AgentContextFactory()

@pytest.fixture
def conversation():
    return AIConversation(title="Test Context Factory")

def test_factory_builds_tool_context(factory, conversation):
    """Verify the factory creates a ToolContext with the correct conversation."""
    context = factory.build(conversation)
    assert isinstance(context, ToolContext)
    assert context.conversation is conversation