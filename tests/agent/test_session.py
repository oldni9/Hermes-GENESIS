"""
===============================================================================
Tests for Agent Session
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.agent.session import AgentSession
from hermes.ai.conversation import AIConversation


def test_agent_session_initialization():
    session = AgentSession()
    assert isinstance(session.conversation, AIConversation)
    assert session.metadata == {}


def test_agent_session_with_conversation():
    conv = AIConversation(title="test")
    session = AgentSession(conversation=conv)
    assert session.conversation is conv
    assert session.conversation.title == "test"


def test_agent_session_metadata():
    session = AgentSession()
    session.metadata["key"] = "value"
    assert session.metadata["key"] == "value"