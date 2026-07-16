"""
===============================================================================
Hermes Local Client
===============================================================================
"""

from hermes.providers.clients.base_client import BaseProviderClient


class LocalClient(BaseProviderClient):

    provider_name = "Local"

    def generate(self, request):

        raise NotImplementedError(
            "Local client not implemented yet."
        )