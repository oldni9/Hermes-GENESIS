"""
===============================================================================
Hermes Execution Node

Represents one executable unit inside an Execution Graph.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionNode:
    """
    One node inside the Hermes Execution Graph.
    """

    id: str

    name: str

    task: str

    payload: Any = None

    priority: int = 50

    capability: str | None = None

    provider: str | None = None

    model: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    completed: bool = False

    failed: bool = False
