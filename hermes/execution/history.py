"""
===============================================================================
Hermes Execution History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ExecutionHistory:
    """
    Stores one execution record.
    """

    task_name: str

    success: bool

    timestamp: float = field(default_factory=time)
