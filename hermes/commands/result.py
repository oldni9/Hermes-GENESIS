"""
===============================================================================
Hermes Command Result

Canonical result returned by every runtime subsystem.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class CommandResult:
    """
    Standard runtime execution result.

    Every subsystem returns this object.
    """

    success: bool

    message: str = ""

    data: object | None = None

    metadata: dict = field(default_factory=dict)
