"""
===============================================================================
Hermes Provider Config Loader

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
import yaml

from hermes.providers.config import ProviderConfig


class ProviderConfigLoader:

    @staticmethod
    def load(path: Path) -> ProviderConfig:

        data = yaml.safe_load(path.read_text())

        return ProviderConfig(**data)