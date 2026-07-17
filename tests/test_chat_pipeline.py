"""
===============================================================================
Tests for HermesClient integration with AIPipeline (Sprint 3 PR1)

Verifies:
    - HermesClient.complete() uses pipeline.execute() when pipeline is provided.
    - HermesClient.complete() falls back to manager.execute() when pipeline is None.
    - Backward compatibility: manager parameter still works.
    - Provider/model overrides are respected.
    - AIContext is built correctly (without unsupported fields).
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec, patch

import pytest

from hermes.ai.client import HermesClient
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
    pipeline = create_autospec(AIPipeline)
    pipeline.execute.return_value = AIResponse(
        success=True,
        result="Pipeline response",
        provider="pipeline",
        model="pipeline-model",
    )
    pipeline.orchestrator = MagicMock()
    pipeline.orchestrator.manager = MagicMock(spec=AIManager)
    return pipeline


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_client_complete_uses_pipeline_when_provided(mock_pipeline: MagicMock) -> None:
    """complete() should call pipeline.execute() when pipeline is given."""
    client = HermesClient(pipeline=mock_pipeline, provider="test-provider")
    response = client.complete("Hello")

    mock_pipeline.execute.assert_called_once()
    call_kwargs = mock_pipeline.execute.call_args[1]
    assert call_kwargs["provider"] == "test-provider"
    assert isinstance(call_kwargs["request"], AIRequest)
    assert "Hello" in call_kwargs["request"].prompt
    assert isinstance(call_kwargs["context"], AIContext)

    assert response.success is True
    assert response.result == "Pipeline response"


def test_client_complete_falls_back_to_manager_when_no_pipeline(mock_manager: MagicMock) -> None:
    """complete() should use manager.execute() when pipeline is None."""
    client = HermesClient(manager=mock_manager, provider="test-provider")
    response = client.complete("Hello")

    mock_manager.execute.assert_called_once()
    call_args = mock_manager.execute.call_args[1]
    assert call_args["provider_name"] == "test-provider"
    assert isinstance(call_args["request"], AIRequest)
    assert "Hello" in call_args["request"].prompt

    assert response.success is True
    assert response.result == "Mock response"


def test_client_complete_with_provider_override_uses_override(mock_pipeline: MagicMock) -> None:
    """Request provider override should take precedence over the default."""
    client = HermesClient(pipeline=mock_pipeline, provider="default-provider")
    client.complete("Hello", provider="override-provider")

    mock_pipeline.execute.assert_called_once()
    call_kwargs = mock_pipeline.execute.call_args[1]
    assert call_kwargs["provider"] == "override-provider"


def test_client_complete_with_model_override_uses_override(mock_pipeline: MagicMock) -> None:
    """Request model override should be set in the request."""
    # Provide a default provider so that _execute_request can resolve one
    client = HermesClient(pipeline=mock_pipeline, provider="test-provider", model="default-model")
    client.complete("Hello", model="override-model")

    mock_pipeline.execute.assert_called_once()
    request = mock_pipeline.execute.call_args[1]["request"]
    assert request.model == "override-model"


def test_client_complete_with_system_instruction(mock_pipeline: MagicMock) -> None:
    """System instruction should be added to the prompt."""
    client = HermesClient(pipeline=mock_pipeline, provider="test-provider")
    client.complete("Hello", system="You are a helpful assistant.")

    mock_pipeline.execute.assert_called_once()
    request = mock_pipeline.execute.call_args[1]["request"]
    messages = request.options.get("messages", [])
    assert any(m["role"] == "system" for m in messages)


def test_client_complete_with_options(mock_pipeline: MagicMock) -> None:
    """Options should be passed to the request."""
    client = HermesClient(pipeline=mock_pipeline, provider="test-provider")
    client.complete("Hello", options={"temperature": 0.5, "max_tokens": 100})

    mock_pipeline.execute.assert_called_once()
    request = mock_pipeline.execute.call_args[1]["request"]
    assert request.options.get("temperature") == 0.5
    assert request.options.get("max_tokens") == 100


def test_client_raises_error_when_no_provider(mock_pipeline: MagicMock) -> None:
    """If no provider is resolved, complete() should raise ValueError."""
    client = HermesClient(pipeline=mock_pipeline)  # no provider set
    with pytest.raises(ValueError, match="No provider specified"):
        client.complete("Hello")


def test_client_without_manager_or_pipeline_creates_default_manager() -> None:
    """If neither pipeline nor manager is given, create a default AIManager."""
    with patch("hermes.ai.client.AIManager") as MockManager:
        MockManager.return_value = MagicMock(spec=AIManager)
        client = HermesClient()
        assert client._manager is not None
        MockManager.assert_called_once()


def test_client_manager_property_returns_manager(mock_manager: MagicMock) -> None:
    """The manager property should return the stored manager."""
    client = HermesClient(manager=mock_manager)
    assert client.manager is mock_manager


def test_client_pipeline_property_returns_pipeline(mock_pipeline: MagicMock) -> None:
    """The pipeline property should return the stored pipeline."""
    client = HermesClient(pipeline=mock_pipeline)
    assert client.pipeline is mock_pipeline


def test_client_chat_passes_pipeline(mock_pipeline: MagicMock) -> None:
    """Chat() should pass the pipeline through to the Chat instance."""
    client = HermesClient(pipeline=mock_pipeline, provider="test")
    chat = client.chat()
    assert chat.pipeline is mock_pipeline
    assert chat.provider == "test"


def test_client_chat_fallback_manager(mock_manager: MagicMock) -> None:
    """Chat() should pass the manager if no pipeline is set."""
    client = HermesClient(manager=mock_manager, provider="test")
    chat = client.chat()
    assert chat.pipeline is None
    assert chat.manager is mock_manager