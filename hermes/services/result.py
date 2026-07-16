"""
===============================================================================
Hermes Service Result

Standard return object for every Hermes service.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ServiceResult:
    """
    Standardized service response.
    """

    success: bool

    message: str = ""

    data: object | None = None

    metadata: dict = field(default_factory=dict)

    execution_time: float = 0.0

    cached: bool = False

    provider: str = ""

    model: str = ""