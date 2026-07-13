"""
===============================================================================
Hermes Runtime Agent
===============================================================================

Agents are executable runtime roles.

An Agent is NOT tied to a specific model.

Instead it describes HOW Hermes should perform
a particular role.

The Scheduler chooses an appropriate RuntimeModel
from the preferred model list.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeAgent:
    """
    Runtime Agent.
    """

    id: str

    name: str

    description: str = ""

    enabled: bool = True

    preferred_models: list[str] = field(default_factory=list)

    capabilities: list[str] = field(default_factory=list)

    scheduler: str = "balanced"

    profile: str = "default"

    temperature: float = 0.7

    max_context: int = 8192

    system_prompt: str = ""

    metadata: dict = field(default_factory=dict)