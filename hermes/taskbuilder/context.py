"""
===============================================================================
Hermes Task Builder Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TaskBuilderContext:
    """
    Intermediate context used while constructing KernelTasks.
    """

    name: str

    payload: Any

    priority: int = 50
