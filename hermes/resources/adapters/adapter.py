"""
===============================================================================
Hermes Runtime Adapter
===============================================================================

Defines a Runtime Adapter Object.

Adapters describe HOW Hermes communicates with external systems.

Runtime Objects contain configuration only.

They never execute requests directly.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeAdapter:
    """
    Runtime description of an external adapter.
    """

    id: str

    name: str

    adapter_type: str = "llm"

    endpoint: str = ""

    enabled: bool = True

    priority: int = 100

    authentication: str = "none"

    plugin: str = ""

    metadata: dict = field(default_factory=dict)
