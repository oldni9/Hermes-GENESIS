"""
===============================================================================
Hermes Runtime Pipeline Stage

Represents one stage inside a pipeline.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeStage:
    """
    One execution stage.

    Examples

        Planner

        Vision

        Reasoner

        Coder

        Reviewer
    """

    name: str

    provider: str

    model: str

    capability: str

    enabled: bool = True

    metadata: dict = field(default_factory=dict)
