"""
===============================================================================
Hermes Runtime Profile History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class RuntimeProfileHistory:
    """
    Records profile activation history.
    """

    profile: str

    timestamp: float = field(default_factory=time)

    duration: float = 0.0
