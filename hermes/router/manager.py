"""
===============================================================================
Hermes Provider Manager
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.providers.enums import ProviderType
from hermes.providers.provider import Provider
from hermes.providers.registry import ProviderRegistry


class ProviderManager:

    def __init__(self) -> None:

        self.registry = ProviderRegistry()

        self._bootstrap()

    # ------------------------------------------------------------------

    def _bootstrap(self) -> None:

        self.registry.register(

            Provider(

                name=ProviderType.LOCAL,

                capabilities=set(CapabilityType),

            )

        )

        self.registry.register(

            Provider(

                name=ProviderType.GROQ,

                capabilities={
                    CapabilityType.CHAT,
                    CapabilityType.REASONING,
                    CapabilityType.CODE,
                },

            )

        )

        self.registry.register(

            Provider(

                name=ProviderType.OPENROUTER,

                capabilities=set(CapabilityType),

            )

        )

        self.registry.register(

            Provider(

                name=ProviderType.ZAI,

                capabilities={
                    CapabilityType.CHAT,
                    CapabilityType.VISION,
                    CapabilityType.REASONING,
                },

            )

        )

        self.registry.register(

            Provider(

                name=ProviderType.CLOUDFLARE,

                capabilities=set(CapabilityType),

            )

        )

    # ------------------------------------------------------------------

    def providers_for(

        self,

        capability: CapabilityType,

    ) -> list[Provider]:

        return [

            provider

            for provider in self.registry.all()

            if capability in provider.capabilities

        ]