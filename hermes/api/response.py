"""
===============================================================================
Hermes Response

Standard response returned by Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(slots=True)
class HermesResponse:
    """
    Public response returned by Hermes.run().
    """

    success: bool

    text: str

    data: Any = None

    metadata: dict[str, Any] = field(default_factory=dict)

    timestamp: float = field(default_factory=time)
