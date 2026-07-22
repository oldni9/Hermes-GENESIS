"""
===============================================================================
Tests for Agent Executor Memory Integration (Sprint 13)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseChoice, ResponseMessage
from hermes.agent.executor import AgentExecutor
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.retrieval import RetrievedMemory, RetrievedContext, MemoryTier
from hermes.ai.tool import ToolManager, ToolRegistry


def make_text_response(text: str):
    choice = ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=text), finish_reason="stop")
    return AIResponse(success=True, result=text, provider="test", model="test-model", choices=[choice])

@pytest.fixture
def mock_pipeline() -> MagicMock:
    return MagicMock(spec=PipelineProtocol)

@pytest.fixture
def tool_manager() -> ToolManager:
    return ToolManager(ToolRegistry())

@pytest.fixture
def mock_memory_manager() -> MagicMock:
    mgr = MagicMock(spec=UnifiedMemoryManager)
    mgr.recall.return_value = RetrievedContext(memories=[
        RetrievedMemory(id="1", tier=MemoryTier.EPISODIC, content="User likes Python", score=0.9)
    ])
    return mgr

def test_executor_retrieves_memory_but_does_not_mutate_system_prompt(mock_pipeline, tool_manager, mock_memory_manager):
    """Executor should query memory manager and pass to state, but NOT mutate system prompt."""
    mock_pipeline.execute.return_value = make_text_response("Done")
    
    agent = AgentExecutor(
        mock_pipeline, 
        tool_manager, 
        "test", "test-model", 
        memory_manager=mock_memory_manager
    )
    
    conv = AIConversation()
    agent.run("Hello", conv, system_prompt="You are helpful.")
    
    # Verify memory manager was queried
    mock_memory_manager.recall.assert_called_once()
    
    # Verify system prompt was NOT mutated
    system_msg = conv.messages()[0]
    assert system_msg.content == "You are helpful."
    assert "User likes Python" not in system_msg.content

def test_executor_does_not_persist_memories_automatically(mock_pipeline, tool_manager, mock_memory_manager):
    """Executor should not automatically remember interactions. Planners own that decision."""
    mock_pipeline.execute.return_value = make_text_response("Done")
    
    agent = AgentExecutor(
        mock_pipeline, 
        tool_manager, 
        "test", "test-model", 
        memory_manager=mock_memory_manager
    )
    
    agent.run("Hello", AIConversation())
    
    # Verify remember was NOT called by the executor
    mock_memory_manager.remember.assert_not_called()