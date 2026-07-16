"""
===============================================================================
Hermes Subsystem Capabilities
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class SubsystemCapabilities:

    commands: list[str] = field(
        default_factory=list,
    )

    supports_background_tasks: bool = False

    supports_notifications: bool = False

    supports_search: bool = False

    supports_ai_control: bool = True