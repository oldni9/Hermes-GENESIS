"""
===============================================================================
Hermes Command

Canonical command object passed throughout the runtime.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class Command:
    """
    Canonical runtime command.

    Every user request eventually becomes one of these.
    """

    text: str

    subsystem: str = ""

    action: str = ""

    arguments: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)