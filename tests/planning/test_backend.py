"""
===============================================================================
Tests for PlanningBackend
===============================================================================
"""
from __future__ import annotations
from unittest.mock import MagicMock
import pytest

from hermes.ai.pipeline import AIPipeline
from hermes.ai.response import AIResponse
from hermes.planning.backend import PipelinePlanningBackend
from hermes.planning.exceptions import PlanningError
from hermes.planning.config import PlanningConfig


@pytest.fixture
def mock_pipeline() -> MagicMock:
    mock = MagicMock(spec=AIPipeline)
    return mock


def test_backend_classify_success(mock_pipeline):
    mock_response = AIResponse(success=True, result="code")
    mock_pipeline.execute.return_value = mock_response

    backend = PipelinePlanningBackend(mock_pipeline)
    domain = backend.classify("Write a function")
    assert domain == "code"


def test_backend_classify_normalizes_whitespace(mock_pipeline):
    mock_response = AIResponse(success=True, result="  code  ")
    mock_pipeline.execute.return_value = mock_response

    backend = PipelinePlanningBackend(mock_pipeline)
    domain = backend.classify("test")
    assert domain == "code"


def test_backend_classify_empty_response(mock_pipeline):
    mock_response = AIResponse(success=True, result="")
    mock_pipeline.execute.return_value = mock_response

    backend = PipelinePlanningBackend(mock_pipeline)
    with pytest.raises(PlanningError, match="Classification failed: Empty response"):
        backend.classify("test")


def test_backend_classify_pipeline_failure(mock_pipeline):
    mock_pipeline.execute.side_effect = ValueError("API down")
    backend = PipelinePlanningBackend(mock_pipeline)
    with pytest.raises(PlanningError, match="Classification failed: API down"):
        backend.classify("test")


def test_backend_with_config(mock_pipeline):
    mock_response = AIResponse(success=True, result="chat")
    mock_pipeline.execute.return_value = mock_response

    config = PlanningConfig(planner_provider="test", planner_model="test-model")
    backend = PipelinePlanningBackend(mock_pipeline, config)
    backend.classify("Hello")

    # Verify the request was passed with the configured provider/model
    call_args = mock_pipeline.execute.call_args[1]
    assert call_args["request"].provider == "test"
    assert call_args["request"].model == "test-model"