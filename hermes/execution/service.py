"""
===============================================================================
Hermes Execution Service

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.providers.manager import ProviderManager
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class ExecutionService:
    """
    Thin execution layer.

    Runtime
        ↓
    ExecutionService
        ↓
    ProviderManager
        ↓
    ProviderDispatcher
        ↓
    Provider Client
    """

    def __init__(
        self,
        provider_manager: ProviderManager,
    ) -> None:

        self.provider_manager = provider_manager

    # ------------------------------------------------------------------

    def execute(

        self,

        prompt: str,

        capability: CapabilityType = CapabilityType.CHAT,

    ) -> ProviderResult:

        request = ProviderRequest(

            prompt=prompt,

        )

        return self.provider_manager.execute(

            request,

            capability,

        )