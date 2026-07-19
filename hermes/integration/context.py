"""
===============================================================================
Hermes Integration Context
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class IntegrationContext:
    """
    Shared runtime context.

    Passed through the integration pipeline.
    """

    prompt: str

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
