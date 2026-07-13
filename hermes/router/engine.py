"""
===============================================================================
Hermes Routing Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.models.manager import ModelManager
from hermes.providers.manager import ProviderManager

from hermes.router.model_resolver import ModelResolver
from hermes.router.candidate_builder import CandidateBuilder
from hermes.router.model_selector import ModelSelector


class RoutingEngine:
    """
    Complete routing pipeline.

        Capability
             ↓
      ModelResolver
             ↓
     CandidateBuilder
             ↓
      ModelSelector
             ↓
           Route
    """

    def __init__(self) -> None:

        # Managers own the registries
        self.model_manager = ModelManager()
        self.provider_manager = ProviderManager()

        # Resolver uses the model manager
        self.models = ModelResolver(
            self.model_manager,
        )

        # Builder only needs the provider registry
        self.builder = CandidateBuilder(
            self.provider_manager.registry,
        )

        self.selector = ModelSelector()

    # ------------------------------------------------------------------

    def resolve(
        self,
        capability: CapabilityType,
    ):

        models = self.models.resolve(
            capability,
        )

        candidates = self.builder.build(
            models,
        )

        return self.selector.select(
            candidates,
        )