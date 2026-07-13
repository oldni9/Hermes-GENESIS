# hermes/kernel/result.py

"""
===============================================================================
Hermes Kernel Result

Result produced by a Kernel Task.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(slots=True)
class TaskResult:
    """
    Result returned after executing a kernel task.
    """

    task_id: str

    success: bool

    output: Any = None

    error: str | None = None

    completed: float = field(default_factory=time)