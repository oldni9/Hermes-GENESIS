"""
===============================================================================
Hermes Task Builder History

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class TaskBuilderHistory:

    task_name: str

    timestamp: float = field(default_factory=time)

    success: bool = True
