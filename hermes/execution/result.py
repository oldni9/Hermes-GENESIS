"""
===============================================================================
Hermes Execution Result

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ExecutionResult:
    """
    Result of executing a runtime task.
    """

    success: bool

    output: Any = None

    error: str | None = None
