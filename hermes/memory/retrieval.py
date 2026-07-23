"""
===============================================================================
Memory Retrieval Models
===============================================================================

Sprint 16 Update:
MemoryCandidate is now frozen (immutable) to prevent mutation during pipeline processing.
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class MemoryTier(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


@dataclass(slots=True)
class RetrievedMemory:
    """Structured representation of a retrieved memory."""
    id: str
    tier: MemoryTier
    content: str
    score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedContext:
    """Context object passed to planners containing retrieved memories and metadata."""
    memories: List[RetrievedMemory]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecallPolicy:
    """Configuration for memory retrieval."""
    tiers: List[MemoryTier] = field(default_factory=lambda: [MemoryTier.EPISODIC, MemoryTier.SEMANTIC])
    top_k: int = 5


@dataclass(frozen=True)
class MemoryCandidate:
    """
    Immutable representation of a piece of information a planner wants to persist.
    Planners emit these instead of calling memory_manager.remember() directly.
    """
    text: str
    importance: float = 0.5
    tier: MemoryTier = MemoryTier.EPISODIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    reason: str = ""
    source_planner: str = ""