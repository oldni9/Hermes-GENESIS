"""
===============================================================================
Tests for Memory Tools
===============================================================================
"""

import pytest
from unittest.mock import MagicMock

from hermes.long_term_memory.tools import MemoryTools
from hermes.long_term_memory.manager import MemoryManager
from hermes.long_term_memory.models import MemoryRecord
from hermes.ai.tool import ToolManager, ParameterType


@pytest.fixture
def memory_tools():
    return MemoryTools(MemoryManager())

def test_remember_tool(memory_tools):
    result = memory_tools.remember(content="Remember this", metadata={"k": "v"})
    assert "Memory saved with ID:" in result
    record_id = result.replace("Memory saved with ID: ", "")
    assert memory_tools.list_memories()[0]["id"] == record_id

def test_forget_tool(memory_tools):
    memory_tools.remember("Forget this")
    rec_id = memory_tools.list_memories()[0]["id"]
    result = memory_tools.forget(record_id=rec_id)
    assert result == "Memory forgotten."
    assert len(memory_tools.list_memories()) == 0

def test_forget_nonexistent(memory_tools):
    result = memory_tools.forget(record_id="fake-id")
    assert result == "Memory ID not found."

def test_search_memories_tool(memory_tools):
    memory_tools.remember("Apple")
    memory_tools.remember("Banana")
    results = memory_tools.search_memories(query="App")
    assert len(results) == 1
    assert results[0]["content"] == "Apple"

def test_list_memories_tool(memory_tools):
    memory_tools.remember("A")
    memory_tools.remember("B")
    assert len(memory_tools.list_memories()) == 2

def test_clear_memory_tool(memory_tools):
    memory_tools.remember("A")
    memory_tools.clear_memory()
    assert len(memory_tools.list_memories()) == 0

def test_register_tools_schema():
    mock_tm = MagicMock(spec=ToolManager)
    mt = MemoryTools(MemoryManager())
    mt.register(mock_tm)
    
    # Verify register_function was called 5 times
    assert mock_tm.register_function.call_count == 5
    
    # Verify the 'forget' tool schema specifically to check parameter renaming
    forget_call = next(c for c in mock_tm.register_function.call_args_list if c.kwargs['name'] == 'forget')
    assert forget_call.kwargs['func'] == mt.forget
    params = forget_call.kwargs['parameters']
    assert len(params) == 1
    assert params[0].name == 'record_id'
    assert params[0].type == ParameterType.STRING
    assert params[0].required is True