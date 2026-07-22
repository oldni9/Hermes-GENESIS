"""
===============================================================================
Unified Memory Manager
===============================================================================

Sprint 13: The Unified Memory Subsystem.
Provides a single facade over Episodic and Semantic memory tiers.
Uses protocols for backends and a processing pipeline for retrieval.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from hermes.memory.interfaces import EpisodicStore, SemanticStore
from hermes.memory.models import MemoryEntry
from hermes.memory.retrieval import RetrievedMemory, RetrievedContext, RecallPolicy, MemoryTier
from hermes.memory.pipeline import MemoryPipeline, Deduplicator, Summarizer, Ranker, TokenBudgetCompressor

logger = logging.getLogger(__name__)


class UnifiedMemoryManager:
    """
    Facade for Hermes memory subsystems.
    Routes remember/recall operations to appropriate backends.
    Working memory is intentionally excluded as it belongs to the execution/runtime layer.
    """
    
    def __init__(
        self, 
        episodic_store: EpisodicStore, 
        semantic_store: Optional[SemanticStore] = None
    ) -> None:
        self._episodic = episodic_store
        self._semantic = semantic_store
        
        # Initialize processing pipeline
        # Order: Deduplicate -> Rank -> Compress -> Summarize
        self._pipeline = MemoryPipeline([
            Deduplicator(),
            Ranker(),
            TokenBudgetCompressor(),
            Summarizer()
        ])

    def remember(
        self, 
        content: str, 
        tier: MemoryTier = MemoryTier.EPISODIC, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Stores content in the specified memory tier."""
        if tier == MemoryTier.EPISODIC:
            entry = MemoryEntry(
                content=content, 
                metadata=metadata or {}
            )
            return self._episodic.add(entry)
            
        elif tier == MemoryTier.SEMANTIC:
            if not self._semantic:
                raise ValueError("Semantic store not configured")
            return self._semantic.remember(text=content, metadata=metadata)
            
        raise ValueError(f"Unknown memory tier: {tier}")

    def recall(
        self, 
        query: str, 
        policy: Optional[RecallPolicy] = None
    ) -> RetrievedContext:
        """Retrieves memories based on the recall policy and processes them through the pipeline."""
        if policy is None:
            policy = RecallPolicy()
            
        results: List[RetrievedMemory] = []
        retrieval_meta: Dict[str, Any] = {"semantic_available": False}
        
        if MemoryTier.EPISODIC in policy.tiers:
            entries = self._episodic.search(query, limit=policy.top_k)
            for e in entries:
                results.append(RetrievedMemory(
                    id=e.id,
                    tier=MemoryTier.EPISODIC,
                    content=e.content,
                    score=e.score,
                    metadata=dict(e.metadata)
                ))
                
        if MemoryTier.SEMANTIC in policy.tiers and self._semantic:
            try:
                docs = self._semantic.search(query=query, top_k=policy.top_k)
                for d in docs:
                    results.append(RetrievedMemory(
                        id=d.id,
                        tier=MemoryTier.SEMANTIC,
                        content=d.text,
                        metadata=dict(d.metadata)
                    ))
                retrieval_meta["semantic_available"] = True
            except Exception as e:
                logger.warning(
                    f"Semantic memory retrieval failed for query '{query}': {e}", 
                    exc_info=True
                )
                retrieval_meta["semantic_available"] = False
                retrieval_meta["semantic_error"] = str(e)
            
        # Run through pipeline
        processed = self._pipeline.run(results)
        final_memories = processed[:policy.top_k]
        
        return RetrievedContext(memories=final_memories, metadata=retrieval_meta)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture