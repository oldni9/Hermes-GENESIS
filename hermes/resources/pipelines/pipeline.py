"""
===============================================================================
Hermes Runtime Pipeline

Represents a Runtime Execution Pipeline.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimePipeline:
    """
    Runtime execution pipeline.

    A pipeline is an ordered collection
    of execution stages.
    """

    name: str

    stages: list[str] = field(default_factory=list)

    enabled: bool = True

    priority: int = 100

    metadata: dict = field(default_factory=dict)
