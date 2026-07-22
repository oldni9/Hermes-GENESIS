"""
===============================================================================
Tests for Unified Memory Manager (Sprint 13)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.retrieval import RetrievedMemory, RetrievedContext, RecallPolicy, MemoryTier
from hermes.memory.backend import MemoryBackend
from hermes.memory.models import MemoryEntry
from hermes.memory.semantic.semantic_memory import SemanticMemory


@pytest.fixture
def mock_episodic():
    store = MagicMock(spec=MemoryBackend)
    store.search.return_value = [
        MemoryEntry(id="ep1", content="Episodic memory", score=0.8)
    ]
    return store

@pytest.fixture
def mock_semantic():
    store = MagicMock(spec=SemanticMemory)
    mock_doc = MagicMock()
    mock_doc.id = "sem1"
    mock_doc.text = "Semantic memory"
    mock_doc.metadata = {}
    store.search.return_value = [mock_doc]
    return store

def test_episodic_memory_add_and_recall(mock_episodic, mock_semantic):
    mgr = UnifiedMemoryManager(mock_episodic, mock_semantic)
    
    mgr.remember("Episodic data", tier=MemoryTier.EPISODIC)
    mock_episodic.add.assert_called_once()
    
    # Use policy to only query episodic so we know exactly how many results to expect
    ctx = mgr.recall("Episodic", policy=RecallPolicy(tiers=[MemoryTier.EPISODIC]))
    mock_episodic.search.assert_called_with("Episodic", limit=5)
    assert isinstance(ctx, RetrievedContext)
    assert len(ctx.memories) == 1
    assert ctx.memories[0].content == "Episodic memory"
    assert ctx.memories[0].tier == MemoryTier.EPISODIC

def test_semantic_memory_add_and_recall(mock_episodic, mock_semantic):
    mgr = UnifiedMemoryManager(mock_episodic, mock_semantic)
    
    mgr.remember("Semantic data", tier=MemoryTier.SEMANTIC)
    mock_semantic.remember.assert_called_once()
    
    # Use policy to only query semantic
    ctx = mgr.recall("Semantic", policy=RecallPolicy(tiers=[MemoryTier.SEMANTIC]))
    mock_semantic.search.assert_called_once()
    assert len(ctx.memories) == 1
    assert ctx.memories[0].content == "Semantic memory"
    assert ctx.memories[0].tier == MemoryTier.SEMANTIC
    assert ctx.metadata["semantic_available"] is True

def test_recall_policy_filters_tiers(mock_episodic, mock_semantic):
    mgr = UnifiedMemoryManager(mock_episodic, mock_semantic)
    
    # Only query episodic
    policy = RecallPolicy(tiers=[MemoryTier.EPISODIC])
    ctx = mgr.recall("test", policy=policy)
    mock_episodic.search.assert_called()
    mock_semantic.search.assert_not_called()
    assert len(ctx.memories) == 1

def test_recall_policy_limits_top_k(mock_episodic, mock_semantic):
    mgr = UnifiedMemoryManager(mock_episodic, mock_semantic)
    
    policy = RecallPolicy(top_k=1)
    # Both episodic and semantic return 1 item each, total 2. top_k=1 should limit to 1.
    ctx = mgr.recall("test", policy=policy)
    assert len(ctx.memories) == 1

def test_recall_default_policy_is_none(mock_episodic, mock_semantic):
    """Ensure passing no policy uses the default RecallPolicy safely."""
    mgr = UnifiedMemoryManager(mock_episodic, mock_semantic)
    ctx = mgr.recall("test")
    # Default policy queries both, so we expect 2 memories (1 from each mock)
    assert len(ctx.memories) == 2

def test_semantic_failure_logs_metadata(mock_episodic):
    """If semantic store fails, context metadata should reflect it."""
    mock_sem_fail = MagicMock(spec=SemanticMemory)
    mock_sem_fail.search.side_effect = Exception("API Error")
    
    mgr = UnifiedMemoryManager(mock_episodic, mock_sem_fail)
    ctx = mgr.recall("test")
    
    assert ctx.metadata["semantic_available"] is False
    # Should still return episodic results
    assert len(ctx.memories) == 1