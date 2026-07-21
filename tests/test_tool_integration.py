"""
===============================================================================
Tests for Tool Integration
===============================================================================
"""

import pytest
import tempfile
from unittest.mock import MagicMock
from hermes.workspace.workspace import Workspace
from hermes.workspace.manager import WorkspaceManager
from hermes.filesystem import LocalFilesystem
from hermes.tools import ToolManager, ToolRegistry, calculate, get_current_time, Tool
from hermes.ai.orchestrator.orchestrator import AIOrchestrator
from hermes.ai.orchestrator.provider_selector import ProviderSelector
from hermes.ai.orchestrator.response_processor import ResponseProcessor
from hermes.ai.orchestrator.retry_policy import RetryPolicy
from hermes.ai.orchestrator.execution_plan import ExecutionPlan
from hermes.ai.manager import AIManager
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolStatus
from hermes.tools.builtin.math_tool import _safe_math_eval

@pytest.fixture
def tool_manager():
    tm = ToolManager(ToolRegistry())
    tm.register_tool(calculate)
    tm.register_tool(get_current_time)
    return tm

def make_tool_response(call_id: str, func_name: str, args: dict = None) -> AIResponse:
    tc = ToolCall(id=call_id, type="function", function=FunctionCall(name=func_name, arguments=args or {}))
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=""),
        finish_reason="tool_calls"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], tool_calls=[tc])

def test_workspace_registers_file_tools(tool_manager):
    """Test that Workspace automatically registers FileTools when FS and TM are present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws = Workspace(filesystem=fs, tool_manager=tool_manager)
        # FIX: workspace_id already starts with ws_, no need to add it again in the assert
        assert tool_manager.exists(f"{ws.workspace_id}.read_file")
        assert tool_manager.exists(f"{ws.workspace_id}.write_file")

        tool = tool_manager.get_tool(f"{ws.workspace_id}.read_file")
        assert tool.name == "read_file"
        assert tool.namespace == ws.workspace_id

def test_orchestrator_executes_tools(tool_manager):
    """Test that the orchestrator executes tool calls via the new ToolManager."""
    mock_provider = MagicMock()
    mock_provider.metadata.name = "test_provider"
    mock_provider.name = "test_provider"
    mock_provider.execute.return_value = make_tool_response("call_1", "calculate", {"expression": "2+2"})
    registry = AIRegistry()
    registry.register(mock_provider)

    orchestrator = AIOrchestrator(
        manager=AIManager(registry),
        provider_selector=ProviderSelector(registry),
        response_processor=ResponseProcessor(),
        retry_policy=RetryPolicy(max_attempts=1),
        tool_manager=tool_manager
    )

    plan = ExecutionPlan(provider="test_provider")
    request = AIRequest(prompt="test", task="chat", provider="test_provider")
    response = orchestrator.execute(request, plan=plan)

    assert "tool_results" in response.metadata
    assert len(response.metadata["tool_results"]) == 1
    assert response.metadata["tool_results"][0].status == ToolStatus.SUCCESS
    assert response.metadata["tool_results"][0].output == "4"

def test_orchestrator_without_tool_manager():
    """Test that the orchestrator works without a tool_manager (backward compatibility)."""
    mock_provider = MagicMock()
    mock_provider.metadata.name = "test_provider"
    mock_provider.name = "test_provider"
    mock_provider.execute.return_value = make_tool_response("call_1", "calculate", {"expression": "2+2"})
    registry = AIRegistry()
    registry.register(mock_provider)

    orchestrator = AIOrchestrator(
        manager=AIManager(registry),
        provider_selector=ProviderSelector(registry),
        response_processor=ResponseProcessor(),
        retry_policy=RetryPolicy(max_attempts=1)
    )

    plan = ExecutionPlan(provider="test_provider")
    request = AIRequest(prompt="test", task="chat", provider="test_provider")
    response = orchestrator.execute(request, plan=plan)

    assert "tool_results" not in response.metadata
    assert len(response.tool_calls) > 0

def test_multiple_workspaces_namespace_isolation(tool_manager):
    """Test that multiple workspaces can register FileTools without collision."""
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        fs1 = LocalFilesystem(tmpdir1)
        fs2 = LocalFilesystem(tmpdir2)
        ws1 = Workspace(filesystem=fs1, tool_manager=tool_manager)
        ws2 = Workspace(filesystem=fs2, tool_manager=tool_manager)

        assert tool_manager.exists(f"{ws1.workspace_id}.read_file")
        assert tool_manager.exists(f"{ws2.workspace_id}.read_file")

        tool1 = tool_manager.get_tool(f"{ws1.workspace_id}.read_file")
        tool2 = tool_manager.get_tool(f"{ws2.workspace_id}.read_file")
        assert tool1 is not tool2
        assert tool1.name == "read_file"
        assert tool1.namespace == ws1.workspace_id

def test_duplicate_workspace_registration(tool_manager):
    """Test that re-initializing a workspace with the same ID does not crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws_id = "ws_duplicate_test"
        ws1 = Workspace(workspace_id=ws_id, filesystem=fs, tool_manager=tool_manager)
        assert tool_manager.exists(f"{ws_id}.read_file")

        ws2 = Workspace(workspace_id=ws_id, filesystem=fs, tool_manager=tool_manager)
        assert tool_manager.exists(f"{ws_id}.read_file")

def test_workspace_deletion_cleans_tools(tool_manager):
    """Test that deleting a workspace unregisters its tools."""
    mgr = WorkspaceManager()
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws = mgr.create_workspace(workspace_id="ws_cleanup", filesystem=fs, tool_manager=tool_manager)

        assert tool_manager.exists("ws_cleanup.read_file")

        result = mgr.delete_workspace("ws_cleanup")
        assert result is True

        assert not tool_manager.exists("ws_cleanup.read_file")
        assert not tool_manager.exists("ws_cleanup.write_file")

def test_workspace_close_is_idempotent(tool_manager):
    """Test that calling close() multiple times does not error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws = Workspace(filesystem=fs, tool_manager=tool_manager)
        ws.close()
        ws.close()

        assert not tool_manager.exists(f"{ws.workspace_id}.read_file")

def test_deleting_multiple_workspaces(tool_manager):
    """Test deleting two workspaces in different orders."""
    mgr = WorkspaceManager()
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        fs1 = LocalFilesystem(tmpdir1)
        fs2 = LocalFilesystem(tmpdir2)

        ws1 = mgr.create_workspace(workspace_id="ws_1", filesystem=fs1, tool_manager=tool_manager)
        ws2 = mgr.create_workspace(workspace_id="ws_2", filesystem=fs2, tool_manager=tool_manager)

        assert tool_manager.exists("ws_1.read_file")
        assert tool_manager.exists("ws_2.read_file")

        mgr.delete_workspace("ws_1")
        assert not tool_manager.exists("ws_1.read_file")
        assert tool_manager.exists("ws_2.read_file")

        mgr.delete_workspace("ws_2")
        assert not tool_manager.exists("ws_2.read_file")

def test_math_tool_rejects_functions():
    """Test that the math tool AST evaluator rejects function calls."""
    with pytest.raises(ValueError):
        _safe_math_eval("sin(1)")
    with pytest.raises(ValueError):
        _safe_math_eval("__import__('os')")

    with pytest.raises(ValueError):
        _safe_math_eval("[1, 2, 3]")

def test_global_vs_workspace_lookup_precedence(tool_manager):
    """Test that global tools and workspace tools can coexist and lookup precedence is correct."""
    global_tool = Tool(name="read_file", function=lambda path: "global")
    tool_manager.register_tool(global_tool)
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws = Workspace(filesystem=fs, tool_manager=tool_manager)

        assert tool_manager.exists("read_file")
        g_tool = tool_manager.get_tool("read_file")
        assert g_tool.function("") == "global"

        ws_tool_name = f"{ws.workspace_id}.read_file"
        assert tool_manager.exists(ws_tool_name)
        ws_tool = tool_manager.get_tool(ws_tool_name)
        assert ws_tool.namespace == ws.workspace_id
        assert ws_tool.name == "read_file"

def test_execution_after_deleting_other_workspace(tool_manager):
    """Test that deleting one workspace does not break execution of another."""
    mgr = WorkspaceManager()
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        fs1 = LocalFilesystem(tmpdir1)
        fs2 = LocalFilesystem(tmpdir2)

        ws1 = mgr.create_workspace(workspace_id="ws_del_1", filesystem=fs1, tool_manager=tool_manager)
        ws2 = mgr.create_workspace(workspace_id="ws_del_2", filesystem=fs2, tool_manager=tool_manager)

        # Write a file to ws2
        write_result = tool_manager.execute_tool(
            f"{ws2.workspace_id}.write_file",
            {"path": "test.txt", "content": "hello"}
        )
        assert write_result.success

        # Delete ws1
        mgr.delete_workspace("ws_del_1")

        # Execute read_file on ws2
        read_result = tool_manager.execute_tool(
            f"{ws2.workspace_id}.read_file",
            {"path": "test.txt"}
        )
        assert read_result.success
        assert read_result.output == "hello"