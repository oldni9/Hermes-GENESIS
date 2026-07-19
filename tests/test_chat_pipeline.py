"""
===============================================================================
Tests for Chat integration with AIPipeline (Sprint 2 PR1)

Verifies:
    - Chat.send() uses pipeline.execute() when pipeline is provided.
    - Chat.send() falls back to manager.execute() when pipeline is None.
    - Backward compatibility: manager parameter still works.
    - Provider/model overrides are respected.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec, patch

import pytest

from hermes.ai.chat import Chat
from hermes.ai.context import AIContext
from hermes.ai.manager import AIManager
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def mock_manager() -> MagicMock:
    """Mock AIManager with a working execute method."""
    manager = create_autospec(AIManager)
    manager.execute.return_value = AIResponse(
        success=True,
        result="Mock response",
        provider="mock",
        model="mock-model",
    )
    return manager


@pytest.fixture
def mock_pipeline() -> MagicMock:
    """Mock AIPipeline with a working execute method."""
    pipeline = create_autospec(AIPipeline)
    pipeline.execute.return_value = AIResponse(
        success=True,
        result="Pipeline response",
        provider="pipeline",
        model="pipeline-model",
    )
    # Simulate orchestrator.manager for compatibility
    pipeline.orchestrator = MagicMock()
    pipeline.orchestrator.manager = MagicMock(spec=AIManager)
    return pipeline


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


def test_chat_send_uses_pipeline_when_provided(mock_pipeline: MagicMock) -> None:
    """Chat.send() should call pipeline.execute() when pipeline is given."""
    _patch_request_to_dict()

    chat = Chat(pipeline=mock_pipeline, provider="test-provider", model="test-model")
    response = chat.send("Hello")

    mock_pipeline.execute.assert_called_once()
    call_kwargs = mock_pipeline.execute.call_args[1]
    assert call_kwargs["provider"] == "test-provider"
    assert isinstance(call_kwargs["request"], AIRequest)
    # The prompt is wrapped with [USER]\n by Prompt.to_request()
    assert "Hello" in call_kwargs["request"].prompt
    assert isinstance(call_kwargs["context"], AIContext)

    assert response.success is True
    assert response.result == "Pipeline response"


def test_chat_send_falls_back_to_manager_when_no_pipeline(
    mock_manager: MagicMock,
) -> None:
    """Chat.send() should use manager.execute() when pipeline is None."""
    _patch_request_to_dict()

    chat = Chat(manager=mock_manager, provider="test-provider", model="test-model")
    response = chat.send("Hello")

    mock_manager.execute.assert_called_once()
    call_args = mock_manager.execute.call_args[1]
    assert call_args["provider_name"] == "test-provider"
    assert isinstance(call_args["request"], AIRequest)
    assert "Hello" in call_args["request"].prompt
    assert call_args["context"] is chat._session  # session passed as context

    assert response.success is True
    assert response.result == "Mock response"


def test_chat_send_with_provider_override_uses_override(
    mock_pipeline: MagicMock,
) -> None:
    """Request provider override should take precedence over the default."""
    _patch_request_to_dict()
    chat = Chat(pipeline=mock_pipeline, provider="default-provider")
    chat.send("Hello", provider="override-provider")

    mock_pipeline.execute.assert_called_once()
    call_kwargs = mock_pipeline.execute.call_args[1]
    assert call_kwargs["provider"] == "override-provider"


def test_chat_send_with_model_override_uses_override(mock_pipeline: MagicMock) -> None:
    """Request model override should be set in the request."""
    _patch_request_to_dict()
    # Provide a provider so that _resolve_provider succeeds
    chat = Chat(pipeline=mock_pipeline, provider="test-provider", model="default-model")
    chat.send("Hello", model="override-model")

    mock_pipeline.execute.assert_called_once()
    request = mock_pipeline.execute.call_args[1]["request"]
    assert request.model == "override-model"


def test_chat_manager_property_returns_manager(mock_manager: MagicMock) -> None:
    """The manager property should return the stored manager (for compatibility)."""
    chat = Chat(manager=mock_manager)
    assert chat.manager is mock_manager


def test_chat_pipeline_property_returns_pipeline(mock_pipeline: MagicMock) -> None:
    """The pipeline property should return the stored pipeline."""
    chat = Chat(pipeline=mock_pipeline)
    assert chat.pipeline is mock_pipeline


def test_chat_without_manager_or_pipeline_uses_default_manager() -> None:
    """
    If neither pipeline nor manager is given, Chat should create a default AIManager.
    (This relies on AIManager having a default constructor; if it doesn't, the test
    will need to patch it – but we assume the original code worked.)
    """
    with patch("hermes.ai.chat.AIManager") as MockManager:
        MockManager.return_value = MagicMock(spec=AIManager)
        chat = Chat()
        assert chat._manager is not None
        MockManager.assert_called_once()  # no arguments


def test_chat_send_raises_error_when_no_provider(mock_pipeline: MagicMock) -> None:
    """If no provider is resolved, send() should raise ValueError."""
    _patch_request_to_dict()
    chat = Chat(pipeline=mock_pipeline)  # no provider set
    with pytest.raises(ValueError, match="No provider specified"):
        chat.send("Hello")


def test_chat_send_raises_error_when_streaming(mock_pipeline: MagicMock) -> None:
    """If a stream is in progress, send() should raise RuntimeError."""
    _patch_request_to_dict()
    chat = Chat(pipeline=mock_pipeline, provider="test")
    # Simulate streaming flag
    chat._streaming_message_id = "fake-stream-id"
    with pytest.raises(RuntimeError, match="streaming is in progress"):
        chat.send("Hello")


# ------------------------------------------------------------------
# Helper: ensure AIRequest.to_dict exists
# ------------------------------------------------------------------


def _patch_request_to_dict() -> None:
    """Add a to_dict method to AIRequest if it doesn't already exist."""
    if not hasattr(AIRequest, "to_dict"):

        def to_dict(self):
            return {
                "prompt": self.prompt,
                "provider": self.provider,
                "model": self.model,
                "options": self.options,
                "metadata": self.metadata,
            }

        AIRequest.to_dict = to_dict
