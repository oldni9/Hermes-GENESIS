"""
===============================================================================
Hermes Integration Context

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class IntegrationContext:
    """
    Shared runtime integration context.
    """

    prompt: str

    metadata: dict[str, Any]