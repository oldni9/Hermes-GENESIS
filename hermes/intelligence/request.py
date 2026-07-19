"""
===============================================================================
Hermes Request
===============================================================================

Represents an incoming request entering the intelligence system.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4


@dataclass(slots=True)
class Request:
    """
    Incoming user request.
    """

    text: str

    id: str = field(default_factory=lambda: str(uuid4()))

    created: float = field(default_factory=time)
