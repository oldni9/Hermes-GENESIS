"""
===============================================================================
Hermes Model Resolver
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.models.manager import ModelManager
from hermes.models.model import Model


class ModelResolver:
    """
    Resolves every compatible model
    for a requested capability.
    """

    def __init__(self):

        self.models = ModelManager()

    # ------------------------------------------------------------------

    def resolve(
        self,
        capability: CapabilityType,
    ) -> list[Model]:

        return self.models.models_for(
            capability,
        )
