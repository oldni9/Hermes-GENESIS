"""
===============================================================================
Tests for AIContext integration (Sprint 3 PR2)

Verifies that AIContext carries session, conversation, memory, and tool
objects when built by Chat and HermesClient.
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.ai.chat import Chat
from hermes.ai.client import HermesClient
from hermes.ai.context import AIContext


def test_chat_build_context_includes_session_and_conversation() -> None:
    """Chat._build_context() should include session and conversation."""
    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(provider="test")
        ctx = chat._build_context()
        assert isinstance(ctx, AIContext)
        assert ctx.session is chat._session
        assert ctx.conversation is chat._conversation
        assert ctx.session_id == chat._session.id
        assert ctx.conversation_id == chat._conversation.id
        assert ctx.provider == chat.provider
        assert ctx.model == chat.model


def test_chat_build_context_with_explicit_objects() -> None:
    """If session/conversation are passed to Chat, they appear in context."""
    session = MagicMock()
    session.id = "custom-session"
    conversation = MagicMock()
    conversation.id = "custom-conv"
    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        chat = Chat(provider="test", session=session, conversation=conversation)
        ctx = chat._build_context()
        assert ctx.session is session
        assert ctx.conversation is conversation
        assert ctx.session_id == "custom-session"
        assert ctx.conversation_id == "custom-conv"


def test_client_build_context_includes_memory_and_tool_manager() -> None:
    """HermesClient._build_context() should include memory and tool_manager."""
    memory = MagicMock()
    tool_manager = MagicMock()
    with patch("hermes.ai.client.AIManager") as MockManager:
        MockManager.return_value = MagicMock()
        client = HermesClient(provider="test", memory=memory, tool_manager=tool_manager)
        ctx = client._build_context()
        assert ctx.memory is memory
        assert ctx.tool_manager is tool_manager
        assert ctx.provider == "test"
        assert ctx.model is None
        # session and conversation are None (client does not own them)
        assert ctx.session is None
        assert ctx.conversation is None


def test_context_copy_preserves_new_fields() -> None:
    """copy() should carry over the new fields."""
    original = AIContext(
        provider="test",
        model="test-model",
        memory=MagicMock(),
        tool_manager=MagicMock(),
        session=MagicMock(),
        conversation=MagicMock(),
    )
    copied = original.copy()
    assert copied.memory is original.memory
    assert copied.tool_manager is original.tool_manager
    assert copied.session is original.session
    assert copied.conversation is original.conversation