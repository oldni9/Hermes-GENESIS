"""
===============================================================================
Hermes Route Score
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.models.model import Model
from hermes.providers.provider import Provider


@dataclass(slots=True)
class RouteScore:
    """
    Represents a scored routing candidate.
    """

    model: Model

    provider: Provider

    score: float

    latency: float = 0.0

    cost: float = 0.0

    health: float = 1.0
