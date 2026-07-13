"""
===============================================================================
Hermes Runtime Preset Profile

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePresetProfile:
    """
    Preset profile.

    Represents the currently active preset.
    """

    name: str

    preset: str

    enabled: bool = True