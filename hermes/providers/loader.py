"""
===============================================================================
Hermes Provider Loader

Loads provider configuration files into the ProviderRegistry.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import yaml

from hermes.providers.registry import ProviderRegistry
from hermes.providers.schemas import ProviderInfo


class ProviderLoader:
    """
    Loads provider YAML definitions into the Provider Registry.
    """

    def __init__(
        self,
        config_directory: Path | None = None,
    ) -> None:

        if config_directory is None:
            self.config_directory = Path(__file__).parent / "configs"
        else:
            self.config_directory = Path(config_directory)

    # ------------------------------------------------------------------

    def load(
        self,
    ) -> ProviderRegistry:

        registry = ProviderRegistry()

        for file in sorted(self.config_directory.glob("*.yaml")):

            with open(
                file,
                "r",
                encoding="utf-8",
            ) as f:

                data = yaml.safe_load(f)

            supports = data.get("supports", {})

            capabilities = [
                capability for capability, enabled in supports.items() if enabled
            ]

            registry.register(
                ProviderInfo(
                    name=data["name"],
                    provider_type=data.get("type", "cloud"),
                    enabled=data.get("enabled", True),
                    priority=data.get("priority", 100),
                    api_base=data.get("connection", {}).get(
                        "base_url",
                        "",
                    ),
                    default_model=data.get("models", {}).get(
                        "default",
                        "",
                    ),
                    models=data.get("models", {}).get(
                        "available",
                        [],
                    ),
                    capabilities=capabilities,
                    metadata={
                        "display_name": data.get(
                            "display_name",
                            "",
                        ),
                        "client": data.get(
                            "client",
                            "",
                        ),
                        "connection": data.get(
                            "connection",
                            {},
                        ),
                    },
                )
            )

        return registry
