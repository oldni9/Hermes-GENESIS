"""
===============================================================================
Hermes Runtime Resource

Base class for every runtime resource.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeResource:
    """
    Base runtime resource.

    Every runtime object inside Hermes derives
    from this class.

    Examples:

        • Model
        • Provider
        • Policy
        • Pipeline
        • Scheduler
        • Profile
        • Preset
    """

    name: str

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)