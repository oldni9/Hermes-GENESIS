"""
===============================================================================
Hermes Genesis Response

Standard response object returned by Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(slots=True)
class Response:
    """
    Standard response produced by Hermes.
    """

    text: str

    success: bool = True

    data: Any = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created: float = field(default_factory=time)

    def __str__(self) -> str:
        return self.text


# Backward compatibility
HermesResponse = Response


__all__ = [
    "Response",
    "HermesResponse",
]