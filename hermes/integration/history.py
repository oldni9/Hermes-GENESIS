"""
===============================================================================
Hermes Integration History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class IntegrationHistory:

    prompt: str

    timestamp: float = field(default_factory=time)

    success: bool = True
