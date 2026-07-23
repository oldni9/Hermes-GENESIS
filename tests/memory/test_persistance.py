"""
===============================================================================
Tests for Memory Persistence Service (Sprint 16)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.persistence import (
    MemoryPersistenceService, 
    CandidateValidator, 
    CandidateNormalizer, 
    CandidateScorer, 
    CandidateDeduplicator
)
from hermes.memory.retrieval import MemoryCandidate, MemoryTier


@pytest.fixture
def mock_memory_manager() -> MagicMock:
    mgr = MagicMock(spec=UnifiedMemoryManager)
    mgr.remember.return_value = "mem_id_123"
    return mgr

@pytest.fixture
def persistence_service(mock_memory_manager: MagicMock) -> MemoryPersistenceService:
    return MemoryPersistenceService(mock_memory_manager)

def test_validator_rejects_empty(persistence_service: MemoryPersistenceService):
    """Validator should drop candidates with empty text."""
    candidates = [
        MemoryCandidate(text="Valid memory", confidence=0.9),
        MemoryCandidate(text="", confidence=0.9),
        MemoryCandidate(text="   ", confidence=0.9)
    ]
    
    stage = CandidateValidator()
    result = stage.process(candidates, None)
    
    assert len(result) == 1
    assert result[0].text == "Valid memory"

def test_validator_rejects_low_confidence(persistence_service: MemoryPersistenceService):
    """Validator should drop candidates with confidence < 0.1."""
    candidates = [
        MemoryCandidate(text="High confidence", confidence=0.5),
        MemoryCandidate(text="Low confidence", confidence=0.05)
    ]
    
    stage = CandidateValidator()
    result = stage.process(candidates, None)
    
    assert len(result) == 1
    assert result[0].text == "High confidence"

def test_normalizer_does_not_mutate_original(persistence_service: MemoryPersistenceService):
    """Normalizer should add normalized_text to metadata without mutating the original candidate."""
    original = MemoryCandidate(text="  Some   Messy   Text  ", confidence=0.9)
    candidates = [original]
    
    stage = CandidateNormalizer()
    result = stage.process(candidates, None)
    
    assert result[0].metadata["normalized_text"] == "some messy text"
    # Verify original is not mutated
    assert "normalized_text" not in original.metadata

def test_scorer_does_not_mutate_original(persistence_service: MemoryPersistenceService):
    """Scorer should calculate persistence_score without mutating the original candidate."""
    original = MemoryCandidate(text="Test", importance=0.8, confidence=0.5)
    candidates = [original]
    
    stage = CandidateScorer()
    result = stage.process(candidates, None)
    
    # Score = 0.8 * (0.5 + 0.5) = 0.8
    assert result[0].metadata["persistence_score"] == 0.8
    # Verify original is not mutated
    assert "persistence_score" not in original.metadata

def test_deduplicator_removes_duplicates(persistence_service: MemoryPersistenceService):
    """Deduplicator should remove candidates with the same normalized text."""
    candidates = [
        MemoryCandidate(text="First Memory", confidence=0.9),
        MemoryCandidate(text="first   memory", confidence=0.8),
        MemoryCandidate(text="Second Memory", confidence=0.9)
    ]
    
    # Run through normalizer first to populate normalized_text
    candidates = CandidateNormalizer().process(candidates, None)
    
    stage = CandidateDeduplicator()
    result = stage.process(candidates, None)
    
    assert len(result) == 2
    assert result[0].text == "First Memory"
    assert result[1].text == "Second Memory"

def test_persistence_service_preserves_planner_metadata(persistence_service: MemoryPersistenceService, mock_memory_manager: MagicMock):
    """Service should preserve planner metadata instead of overwriting it."""
    candidates = [
        MemoryCandidate(
            text="Valid memory", 
            confidence=0.9, 
            importance=0.8, 
            source_planner="ReAct",
            metadata={"entity": "OpenAI", "conversation": "abc"}
        )
    ]
    
    persistence_service.persist(candidates, None)
    
    mock_memory_manager.remember.assert_called_once()
    args, kwargs = mock_memory_manager.remember.call_args
    
    assert kwargs["metadata"]["entity"] == "OpenAI"
    assert kwargs["metadata"]["conversation"] == "abc"
    assert kwargs["metadata"]["source_planner"] == "ReAct"
    assert kwargs["metadata"]["persistence_score"] == 0.8 * (0.5 + 0.9)

def test_persistence_service_integration(persistence_service: MemoryPersistenceService, mock_memory_manager: MagicMock):
    """Service should process candidates and call memory_manager.remember."""
    candidates = [
        MemoryCandidate(text="Valid memory", confidence=0.9, importance=0.8, source_planner="ReAct")
    ]
    
    stored_ids = persistence_service.persist(candidates, None)
    
    assert len(stored_ids) == 1
    assert stored_ids[0] == "mem_id_123"
    mock_memory_manager.remember.assert_called_once()
    
    args, kwargs = mock_memory_manager.remember.call_args
    assert kwargs["content"] == "Valid memory"
    assert kwargs["tier"] == MemoryTier.EPISODIC
    assert kwargs["metadata"]["source_planner"] == "ReAct"
    assert kwargs["metadata"]["persistence_score"] == 0.8 * (0.5 + 0.9)

def test_persistence_service_empty_candidates(persistence_service: MemoryPersistenceService, mock_memory_manager: MagicMock):
    """Service should handle empty candidate list gracefully."""
    stored_ids = persistence_service.persist([], None)
    
    assert len(stored_ids) == 0
    mock_memory_manager.remember.assert_not_called()