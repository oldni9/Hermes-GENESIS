"""
===============================================================================
Hermes Provider Factory
===============================================================================
"""

from __future__ import annotations

from hermes.providers.base import MockProviderClient
from hermes.providers.client import BaseProviderClient
from hermes.providers.enums import ProviderType


class ProviderFactory:

    def create(
        self,
        provider: ProviderType,
    ) -> BaseProviderClient:

        #
        # Temporary.
        #
        # Every provider returns the mock client.
        #

        return MockProviderClient()