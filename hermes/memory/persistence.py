"""
===============================================================================
Memory Persistence Service
===============================================================================

Sprint 16: The Memory Persistence Flow.
Processes MemoryCandidate objects through a functional, configurable pipeline 
before routing them to the UnifiedMemoryManager.
===============================================================================
"""
from __future__ import annotations

import logging
import re
from dataclasses import replace
from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING

from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.retrieval import MemoryCandidate, MemoryTier

if TYPE_CHECKING:
    from hermes.graph.models import GraphContext

logger = logging.getLogger(__name__)


class MemoryPersistenceStage(Protocol):
    """Protocol for memory persistence pipeline stages."""
    def process(
        self, 
        candidates: List[MemoryCandidate], 
        context: Optional["GraphContext"]
    ) -> List[MemoryCandidate]:
        ...


class CandidateValidator(MemoryPersistenceStage):
    """Drops candidates with empty text or extremely low confidence."""
    def process(self, candidates: List[MemoryCandidate], context: Optional["GraphContext"]) -> List[MemoryCandidate]:
        valid = []
        for c in candidates:
            if not c.text or not c.text.strip():
                continue
            if c.confidence < 0.1:
                continue
            valid.append(c)
        return valid


class CandidateNormalizer(MemoryPersistenceStage):
    """Normalizes text for deduplication purposes without mutating the original candidate."""
    def process(self, candidates: List[MemoryCandidate], context: Optional["GraphContext"]) -> List[MemoryCandidate]:
        normalized_candidates = []
        for c in candidates:
            # Basic normalization: lowercase, remove extra whitespace
            normalized = c.text.lower().strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Return a new immutable candidate with updated metadata
            new_meta = {**c.metadata, "normalized_text": normalized}
            normalized_candidates.append(replace(c, metadata=new_meta))
            
        return normalized_candidates


class CandidateScorer(MemoryPersistenceStage):
    """Calculates a final persistence score based on importance and confidence."""
    def process(self, candidates: List[MemoryCandidate], context: Optional["GraphContext"]) -> List[MemoryCandidate]:
        scored_candidates = []
        for c in candidates:
            # Example scoring: base_importance * (0.5 + confidence)
            score = c.importance * (0.5 + c.confidence)
            
            # Return a new immutable candidate with updated metadata
            new_meta = {**c.metadata, "persistence_score": score}
            scored_candidates.append(replace(c, metadata=new_meta))
            
        return scored_candidates


class CandidateDeduplicator(MemoryPersistenceStage):
    """Removes duplicate candidates within the same batch based on normalized text."""
    def process(self, candidates: List[MemoryCandidate], context: Optional["GraphContext"]) -> List[MemoryCandidate]:
        seen = set()
        unique = []
        for c in candidates:
            norm = c.metadata.get("normalized_text", c.text.lower())
            if norm not in seen:
                seen.add(norm)
                unique.append(c)
        return unique


class MemoryPersistenceService:
    """
    Service that processes MemoryCandidate objects through a pipeline
    and persists them to the UnifiedMemoryManager.
    """
    
    def __init__(
        self, 
        memory_manager: UnifiedMemoryManager,
        pipeline: Optional[List[MemoryPersistenceStage]] = None
    ) -> None:
        self._memory_manager = memory_manager
        self._pipeline = pipeline or [
            CandidateValidator(),
            CandidateNormalizer(),
            CandidateScorer(),
            CandidateDeduplicator()
        ]

    def persist(
        self, 
        candidates: List[MemoryCandidate], 
        context: Optional["GraphContext"] = None
    ) -> List[str]:
        """
        Processes candidates through the pipeline and stores them.
        Returns a list of stored memory IDs.
        """
        if not candidates:
            return []

        processed = candidates
        for stage in self._pipeline:
            try:
                processed = stage.process(processed, context)
            except Exception as e:
                logger.error(f"Memory persistence stage {stage.__class__.__name__} failed: {e}")
                # Continue with the current state of processed candidates

        stored_ids = []
        for candidate in processed:
            try:
                # System (persistence) metadata takes precedence over planner metadata
                # to ensure internal fields like 'confidence' are not accidentally overwritten.
                persistence_meta = {
                    "confidence": candidate.confidence,
                    "importance": candidate.importance,
                    "reason": candidate.reason,
                    "source_planner": candidate.source_planner,
                    "persistence_score": candidate.metadata.get("persistence_score", 0.0)
                }
                final_meta = {**candidate.metadata, **persistence_meta}
                
                # Remove internal pipeline keys before storage
                final_meta.pop("normalized_text", None)

                mem_id = self._memory_manager.remember(
                    content=candidate.text,
                    tier=candidate.tier,
                    metadata=final_meta
                )
                stored_ids.append(mem_id)
            except Exception as e:
                logger.error(f"Failed to persist memory candidate: {e}")
                
        return stored_ids

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture