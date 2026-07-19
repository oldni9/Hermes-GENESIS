"""
===============================================================================
Hermes Route

Represents the final routing decision.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.router.capability import ModelCapability


@dataclass(slots=True)
class Route:
    """
    Final routing decision.

        Capability
              +
        Provider
              +
          Model
    """

    capability: ModelCapability

    provider: str

    model: str
