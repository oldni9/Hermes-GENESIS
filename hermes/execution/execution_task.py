"""
===============================================================================
Hermes Execution Task

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionTask:
    """
    Runtime executable task.
    """

    name: str

    payload: dict[str, Any] = field(default_factory=dict)