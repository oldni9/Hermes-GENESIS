"""
===============================================================================
Hermes Runtime Policy History
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class RuntimePolicyHistory:

    policy: str

    timestamp: float = field(default_factory=time)

    allowed: bool = True

    reason: str = ""