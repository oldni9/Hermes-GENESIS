"""
===============================================================================
Tests for Workspace Context & Manager
===============================================================================
"""

import pytest
import tempfile
from hermes.workspace.context import ExecutionContext
from hermes.workspace.workspace import Workspace
from hermes.workspace.manager import WorkspaceManager
from hermes.long_term_memory.manager import MemoryManager
from hermes.filesystem import LocalFilesystem
from hermes.artifacts import LocalArtifactRegistry
from hermes.terminal import LocalTerminal
from hermes.sandbox import LocalSandbox
from hermes.python_workspace import LocalPythonWorkspace
from hermes.tools import ToolManager, ToolRegistry


def test_execution_context_creation():
    ctx = ExecutionContext.create(workspace_id="ws_123", metadata={"user": "test"})
    assert ctx.execution_id.startswith("exec_")
    assert ctx.workspace_id == "ws_123"
    assert ctx.metadata == {"user": "test"}
    assert ctx.start_time > 0

def test_execution_context_immutability():
    ctx = ExecutionContext.create(workspace_id="ws_123")
    with pytest.raises(Exception):
        ctx.execution_id = "new_id"  # type: ignore

def test_workspace_creation():
    ws = Workspace()
    assert ws.workspace_id.startswith("ws_")
    assert isinstance(ws.memory, MemoryManager)
    assert ws.filesystem is None
    assert ws.artifact_registry is None
    assert ws.terminal is None
    assert ws.python_workspace is None
    assert ws.tool_manager is None
    assert len(ws.execution_history) == 0

def test_workspace_custom_id_and_memory():
    mem = MemoryManager()
    ws = Workspace(workspace_id="custom_ws", memory_manager=mem)
    assert ws.workspace_id == "custom_ws"
    assert ws.memory is mem

def test_workspace_filesystem_injection():
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        ws = Workspace(filesystem=fs)
        assert ws.filesystem is fs
        ws.filesystem.write("test.txt", "hello")
        assert ws.filesystem.read("test.txt") == "hello"

def test_workspace_artifact_registry_injection():
    registry = LocalArtifactRegistry()
    ws = Workspace(artifact_registry=registry)
    assert ws.artifact_registry is registry

def test_workspace_terminal_injection():
    term = LocalTerminal(LocalSandbox())
    ws = Workspace(terminal=term)
    assert ws.terminal is term

def test_workspace_python_workspace_injection():
    term = LocalTerminal(LocalSandbox())
    py_ws = LocalPythonWorkspace(term)
    ws = Workspace(python_workspace=py_ws)
    assert ws.python_workspace is py_ws

def test_workspace_tool_manager_injection():
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = ToolManager(ToolRegistry())
        fs = LocalFilesystem(tmpdir)
        ws = Workspace(filesystem=fs, tool_manager=tm)
        # FIX: workspace_id already starts with "ws_", no need to add it again
        assert tm.exists(f"{ws.workspace_id}.read_file")
        assert tm.exists(f"{ws.workspace_id}.write_file")

def test_workspace_execution_history():
    ws = Workspace()
    ctx1 = ws.create_execution(metadata={"run": 1})
    ctx2 = ws.create_execution(metadata={"run": 2})
    
    assert len(ws.execution_history) == 2
    assert ws.execution_history[0].execution_id == ctx1.execution_id
    assert ws.execution_history[1].execution_id == ctx2.execution_id
    
    fetched = ws.get_execution(ctx1.execution_id)
    assert fetched is not None
    assert fetched.metadata == {"run": 1}
    
    assert ws.get_execution("nonexistent") is None

def test_workspace_manager_crud():
    mgr = WorkspaceManager()
    
    ws1 = mgr.create_workspace()
    ws2 = mgr.create_workspace("explicit_id")
    assert len(mgr.list_workspaces()) == 2
    
    assert mgr.get_workspace(ws1.workspace_id) is ws1
    assert mgr.get_workspace("explicit_id") is ws2
    assert mgr.get_workspace("fake") is None
    
    assert mgr.delete_workspace("explicit_id") is True
    assert mgr.delete_workspace("fake") is False
    assert len(mgr.list_workspaces()) == 1

def test_workspace_manager_duplicate_id():
    mgr = WorkspaceManager()
    mgr.create_workspace("unique_id")
    with pytest.raises(ValueError, match="already exists"):
        mgr.create_workspace("unique_id")