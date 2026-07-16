"""
===============================================================================
Hermes Integration Result

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class IntegrationResult:
    """
    Result produced by the Integration layer.
    """

    output: Any

    metadata: dict[str, Any]