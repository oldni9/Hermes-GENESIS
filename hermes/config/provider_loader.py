"""
===============================================================================
Hermes Provider Loader
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from hermes.config.provider_config import ProviderConfig
from hermes.config.yaml_loader import YAMLLoader


class ProviderLoader:

    def __init__(self) -> None:

        self.yaml = YAMLLoader()

        self.directory = Path(__file__).resolve().parents[2] / "knowledge" / "providers"

    # ------------------------------------------------------------------

    def load(
        self,
        provider: str,
    ) -> ProviderConfig:

        file = self.directory / f"{provider}.yaml"

        data = self.yaml.load(
            str(file),
        )

        return ProviderConfig(
            data=data,
        )
