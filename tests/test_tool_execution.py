"""
===============================================================================
Integration tests for Tool Execution in AIOrchestrator (Sprint 4 PR1)

Verifies:
    - Tools are executed when response contains tool_calls and tool_manager is set.
    - Tool results are attached to metadata.
    - When tool_manager is None, tools are not executed.
    - Multiple tool calls, partial failures, and missing tools are handled.
    - Conversion errors produce failed ToolResult with correct call_id.
    - Response is not mutated.
    - Ordering: ResponseProcessor runs before ToolManager.
    - Context propagation.
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.ai.metadata import AIMetadata
from hermes.ai.orchestrator import AIOrchestrator, ExecutionPlan, ProviderSelector, ResponseProcessor, RetryPolicy
from hermes.ai.provider import BaseAIProvider
from hermes.ai.tool import ToolContext
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ToolCall as ProviderToolCall, FunctionCall
from hermes.ai.tool import ToolManager, ToolRegistry, ToolResult, ToolStatus
from hermes.core.exceptions import ProviderError


# ---------- Mock Providers ----------

class MockProviderWithToolCalls(BaseAIProvider):
    def __init__(self, name: str = "mock", tool_calls: list[ProviderToolCall] | None = None):
        super().__init__()
        self._name = name
        self._metadata = AIMetadata(name=name, provider=name, capabilities=["chat"], enabled=True)
        self._tool_calls = tool_calls or [
            ProviderToolCall(id="call_123", type="function",
                             function=FunctionCall(name="test_tool", arguments={"arg": "value1"}))
        ]

    @property
    def metadata(self) -> AIMetadata:
        return self._metadata

    def execute(self, request: AIRequest, context=None) -> AIResponse:
        return AIResponse(success=True, result="Tool call", provider=self._name,
                          model="mock-model", tool_calls=self._tool_calls)


class MockProviderNoToolCalls(BaseAIProvider):
    def __init__(self, name: str = "mock"):
        super().__init__()
        self._metadata = AIMetadata(name=name, provider=name, capabilities=["chat"], enabled=True)

    @property
    def metadata(self) -> AIMetadata:
        return self._metadata

    def execute(self, request: AIRequest, context=None) -> AIResponse:
        return AIResponse(success=True, result="No tools", provider=self._name, model="mock-model")


class MockProviderThatErrors(BaseAIProvider):
    def __init__(self, name: str = "error"):
        super().__init__()
        self._metadata = AIMetadata(name=name, provider=name, capabilities=["chat"], enabled=True)

    @property
    def metadata(self) -> AIMetadata:
        return self._metadata

    def execute(self, request: AIRequest, context=None) -> AIResponse:
        raise ProviderError("Provider failed")


# ---------- Dummy Tools ----------

def dummy_tool(arg: str) -> str:
    return f"Tool executed with {arg}"

def failing_tool(arg: str) -> str:
    raise ValueError("Tool failed intentionally")


# ---------- Fixtures ----------

@pytest.fixture
def registry_with_provider():
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test"))
    return registry

@pytest.fixture
def orchestrator_with_tools(registry_with_provider):
    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="test_tool", func=dummy_tool, description="Test",
                                   parameters=[{"name": "arg", "type": "string", "required": True}])

    selector = ProviderSelector(registry_with_provider)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    # Correct signature: provider_name, request, context
    manager.execute.side_effect = lambda provider_name, request, context=None: registry_with_provider.get(provider_name).execute(request, context)

    return AIOrchestrator(manager, selector, processor, retry, tool_manager)


# ---------- Tests ----------

def test_single_tool_execution(orchestrator_with_tools):
    request = AIRequest(prompt="Use tool", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator_with_tools.execute(request, plan)

    assert "tool_results" in response.metadata
    results = response.metadata["tool_results"]
    assert len(results) == 1
    assert isinstance(results[0], ToolResult)
    assert results[0].status == ToolStatus.SUCCESS
    assert "Tool executed with value1" in results[0].output


def test_multiple_tool_calls():
    tc1 = ProviderToolCall(id="c1", type="function", function=FunctionCall(name="t1", arguments={"arg": "a"}))
    tc2 = ProviderToolCall(id="c2", type="function", function=FunctionCall(name="t2", arguments={"arg": "b"}))
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test", tool_calls=[tc1, tc2]))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="t1", func=lambda arg: f"res1:{arg}")
    tool_manager.register_function(name="t2", func=lambda arg: f"res2:{arg}")

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Multi", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 2
    assert results[0].output == "res1:a"
    assert results[1].output == "res2:b"


def test_missing_tool():
    # Tool not registered
    tool_manager = ToolManager(ToolRegistry())  # empty
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test"))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Missing", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 1
    assert results[0].status == ToolStatus.FAILED
    assert "not found" in results[0].error.lower()


def test_partial_failure():
    tc1 = ProviderToolCall(id="c1", type="function", function=FunctionCall(name="good", arguments={"arg": "x"}))
    tc2 = ProviderToolCall(id="c2", type="function", function=FunctionCall(name="bad", arguments={"arg": "y"}))
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test", tool_calls=[tc1, tc2]))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="good", func=lambda arg: f"good:{arg}")
    tool_manager.register_function(name="bad", func=failing_tool)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Partial", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 2
    assert results[0].status == ToolStatus.SUCCESS
    assert results[0].output == "good:x"
    assert results[1].status == ToolStatus.FAILED
    assert "Tool failed intentionally" in results[1].error


def test_conversion_error():
    # Provider returns arguments as a list (unsupported)
    tc = ProviderToolCall(id="bad_id", type="function", function=FunctionCall(name="test", arguments=["invalid"]))
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test", tool_calls=[tc]))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="test", func=lambda: "should not be called")

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Bad", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 1
    assert results[0].call_id == "bad_id"
    assert results[0].status == ToolStatus.FAILED
    assert "Invalid arguments" in results[0].error


def test_json_string_arguments():
    tc = ProviderToolCall(id="c1", type="function", function=FunctionCall(name="test", arguments='{"arg":"value"}'))
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test", tool_calls=[tc]))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="test", func=lambda arg: f"Got {arg}")

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="JSON", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 1
    assert results[0].status == ToolStatus.SUCCESS
    assert "Got value" in results[0].output


def test_empty_arguments():
    tc = ProviderToolCall(id="c1", type="function", function=FunctionCall(name="test", arguments=""))
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test", tool_calls=[tc]))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="test", func=lambda: "called")

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Empty", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    results = response.metadata["tool_results"]
    assert len(results) == 1
    assert results[0].status == ToolStatus.SUCCESS
    assert "called" in results[0].output


def test_no_tool_calls():
    registry = AIRegistry()
    registry.register(MockProviderNoToolCalls("test"))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)
    tool_manager = ToolManager(ToolRegistry())
    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)

    request = AIRequest(prompt="No tool", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    assert "tool_results" not in response.metadata


def test_tool_manager_none():
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test"))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager=None)
    request = AIRequest(prompt="Skip", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    assert "tool_results" not in response.metadata
    # Original tool_calls should still be present
    assert len(response.tool_calls) == 1


def test_provider_error_prevents_tool_execution():
    registry = AIRegistry()
    registry.register(MockProviderThatErrors("error"))
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)

    tool_manager = MagicMock(spec=ToolManager)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Fail", task="chat")
    plan = ExecutionPlan(provider="error")
    response = orchestrator.execute(request, plan)

    assert response.success is False
    assert "Provider failed" in response.message
    tool_manager.execute_batch.assert_not_called()
    assert "tool_results" not in response.metadata


def test_response_tool_calls_not_mutated():
    registry = AIRegistry()
    provider = MockProviderWithToolCalls("test")
    registry.register(provider)
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="test_tool", func=lambda: "ok")

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="No mutation", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    original_tool_calls = response.tool_calls
    assert len(original_tool_calls) == 1
    assert response.tool_calls is original_tool_calls


def test_ordering_responseprocessor_before_tools():
    registry = AIRegistry()
    registry.register(MockProviderWithToolCalls("test"))
    selector = ProviderSelector(registry)
    retry = RetryPolicy(max_attempts=1)

    parent = MagicMock()
    processor = ResponseProcessor()
    original_process = processor.process

    def process_wrapper(raw_response, provider_name, model_name, start_time):
        parent.processor_called()
        return original_process(raw_response, provider_name, model_name, start_time)
    processor.process = process_wrapper

    tool_manager = MagicMock(spec=ToolManager)
    def execute_batch_wrapper(calls, context):
        parent.tool_called()
        return [ToolResult(call_id=c.id, status=ToolStatus.SUCCESS, output="ok") for c in calls]
    tool_manager.execute_batch.side_effect = execute_batch_wrapper

    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Order", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan)

    expected_order = [call.processor_called(), call.tool_called()]
    assert parent.mock_calls == expected_order


def test_context_propagation():
    # Create a context object with a unique marker
    marker = "unique_marker"
    ctx = ToolContext(metadata={"marker": marker})

    # Provider that returns a tool call
    tc = ProviderToolCall(id="ctx", function=FunctionCall(name="context_tool", arguments={}))
    provider = MockProviderWithToolCalls("test", tool_calls=[tc])
    registry = AIRegistry()
    registry.register(provider)

    # Tool that checks context
    received_context = None
    def context_aware_tool(context=None):
        nonlocal received_context
        received_context = context
        return "ok"

    tool_registry = ToolRegistry()
    tool_manager = ToolManager(tool_registry)
    tool_manager.register_function(name="context_tool", func=context_aware_tool, description="")

    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry = RetryPolicy(max_attempts=1)
    manager = MagicMock()
    manager.execute.side_effect = lambda provider_name, request, context=None: registry.get(provider_name).execute(request, context)

    orchestrator = AIOrchestrator(manager, selector, processor, retry, tool_manager)
    request = AIRequest(prompt="Context", task="chat")
    plan = ExecutionPlan(provider="test")
    response = orchestrator.execute(request, plan, context=ctx)

    # Verify context was passed to the tool
    assert received_context is ctx
    assert received_context.metadata.get("marker") == "unique_marker"
    assert response.metadata["tool_results"][0].status == ToolStatus.SUCCESS