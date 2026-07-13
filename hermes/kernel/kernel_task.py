"""
===============================================================================
Hermes Kernel Task

Represents a single executable unit of work.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class KernelTask:
    """
    Smallest executable unit inside Hermes.
    """

    name: str

    payload: Any = None

    priority: int = 50

    id: str = field(default_factory=lambda: str(uuid4()))

    created: float = field(default_factory=time)