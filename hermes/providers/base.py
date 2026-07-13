"""
===============================================================================
Hermes Mock Provider Client
===============================================================================
"""

from __future__ import annotations

from hermes.providers.client import BaseProviderClient
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class MockProviderClient(BaseProviderClient):

    def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        return ProviderResult(
            success=True,
            text=f"[Mock Provider] {request.prompt}",
        )