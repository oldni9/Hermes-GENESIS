"""
===============================================================================
Hermes Runtime Pipeline History

Stores execution history.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class RuntimePipelineHistory:

    pipeline: str

    timestamp: float = field(default_factory=time)

    success: bool = True

    duration: float = 0.0