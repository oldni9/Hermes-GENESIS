import pytest
from hermes.tools import ToolManager, ToolRegistry, calculate, ToolExecutionResult, ToolContext

def test_tool_manager_execution():
    mgr = ToolManager(ToolRegistry())
    mgr.register_tool(calculate)
    result = mgr.execute_tool("calculate", {"expression": "10 / 2"})
    assert isinstance(result, ToolExecutionResult)
    assert result.success
    assert result.output == "5.0"

def test_tool_manager_execution_id_propagation():
    mgr = ToolManager(ToolRegistry())
    mgr.register_tool(calculate)
    ctx = ToolContext(metadata={"execution_id": "exec_123"})
    result = mgr.execute_tool("calculate", {"expression": "1+1"}, context=ctx)
    assert result.execution_id == "exec_123"