"""
===============================================================================
Hermes Client Factory

Creates provider client instances lazily.

Provider SDKs are imported only when required.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import importlib

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.provider import Provider


class ClientFactory:
    """
    Lazy provider client factory.

    Provider SDKs are imported only when required.
    """

    _MODULES = {
        "gemini": ("gemini_client", "GeminiClient"),
        "groq": ("groq_client", "GroqClient"),
        "openrouter": ("openrouter_client", "OpenRouterClient"),
        "ollama": ("ollama_client", "OllamaClient"),
        "lmstudio": ("lmstudio_client", "LMStudioClient"),
        "local": ("local_client", "LocalClient"),
        "cloudflare": ("cloudflare_client", "CloudflareClient"),
        "zai": ("zai_client", "ZAIClient"),
    }

    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        provider: Provider,
    ) -> BaseProviderClient:

        name = provider.name.lower()

        if name not in cls._MODULES:
            raise ValueError(
                f"Unknown provider '{name}'."
            )

        module_name, class_name = cls._MODULES[name]

        module = importlib.import_module(
            f"hermes.providers.clients.{module_name}"
        )

        client_class = getattr(
            module,
            class_name,
        )

        return client_class(
            provider_name=provider.name,
            api_key=provider.api_key,
            base_url=provider.base_url,
            model=provider.default_model,
        )