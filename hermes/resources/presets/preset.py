"""
===============================================================================
Hermes Runtime Preset

Represents a complete saved Hermes workspace.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimePreset:
    """
    Saved Hermes configuration.

    Presets capture the entire runtime state.
    """

    name: str

    enabled: bool = True

    profile: str = "default"

    metadata: dict = field(default_factory=dict)