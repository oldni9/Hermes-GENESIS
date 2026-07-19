"""
===============================================================================
Memory Models
===============================================================================

Dependencies:
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - MemoryRecord

Public API:
    - MemoryRecord

TODO:
    - Add support for embeddings/vector representations.
    - Add support for memory expiration (TTL).
===============================================================================
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryRecord:
    """
    A single record in long-term memory.
    """
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)