"""
===============================================================================
Hermes Execution Edge

Represents a dependency between execution nodes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionEdge:
    """
    Dependency between two nodes.
    """

    source: str

    target: str
