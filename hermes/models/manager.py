"""
===============================================================================
Hermes Model Manager
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType
from hermes.models.enums import ModelType
from hermes.models.model import Model
from hermes.models.registry import ModelRegistry
from hermes.providers.enums import ProviderType


class ModelManager:

    def __init__(self):

        self.registry = ModelRegistry()

        self._bootstrap()

    # ------------------------------------------------------------------

    def _bootstrap(self):

        self.registry.register(
            Model(
                name=ModelType.LLAMA32,
                provider=ProviderType.LOCAL,
                capabilities={
                    CapabilityType.CHAT,
                    CapabilityType.CODE,
                },
                priority=100,
            )
        )

        self.registry.register(
            Model(
                name=ModelType.GLM47_FLASH,
                provider=ProviderType.ZAI,
                capabilities=set(CapabilityType),
                priority=95,
            )
        )

        self.registry.register(
            Model(
                name=ModelType.GLM52,
                provider=ProviderType.CLOUDFLARE,
                capabilities=set(CapabilityType),
                priority=98,
            )
        )

    # ------------------------------------------------------------------

    def models_for(
        self,
        capability: CapabilityType,
    ) -> list[Model]:

        models = [
            model
            for model in self.registry.all()
            if (
                model.enabled
                and capability in model.capabilities
            )
        ]

        models.sort(
            key=lambda m: m.priority,
            reverse=True,
        )

        return models

    # ------------------------------------------------------------------

    def resolve(
        self,
        capability: CapabilityType,
    ) -> Model:

        models = self.models_for(
            capability,
        )

        if not models:
            raise RuntimeError(
                f"No model supports {capability}"
            )

        return models[0]