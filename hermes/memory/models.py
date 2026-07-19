"""
===============================================================================
Hermes Memory Models
===============================================================================
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple


@dataclass(slots=True, frozen=True)
class MemoryEntry:
    """
    A single memory entry.
    Immutable.
    """
    id: str = ""
    content: str = ""
    tags: Tuple[str, ...] = field(default_factory=tuple)
    timestamp: float = field(default_factory=time.time)
    score: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)