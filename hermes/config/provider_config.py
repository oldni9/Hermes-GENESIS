"""
===============================================================================
Hermes Provider Configuration
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProviderConfig:
    """
    Raw provider configuration loaded from YAML.

    Hermes keeps the original provider snapshot instead
    of flattening everything.
    """

    data: dict[str, Any]

    @property
    def provider(self) -> dict:
        return self.data["provider"]

    @property
    def metadata(self) -> dict:
        return self.data.get("metadata", {})

    @property
    def compatibility(self) -> dict:
        return self.data.get("compatibility", {})

    @property
    def sdk(self) -> dict:
        return self.data.get("sdk", {})

    @property
    def authentication(self) -> dict:
        return self.data.get("authentication", {})

    @property
    def base_urls(self) -> dict:
        return self.data.get("base_urls", {})

    @property
    def features(self) -> dict:
        return self.data.get("features", {})

    @property
    def recommended_models(self) -> dict:
        return self.data.get("recommended_models", {})

    @property
    def models(self) -> list:
        return self.data.get("models", [])

    @property
    def limits(self) -> dict:
        return self.data.get("limits", {})

    @property
    def account(self) -> dict:
        return self.data.get("account", {})

    @property
    def testing(self) -> dict:
        return self.data.get("testing", {})

    @property
    def notes(self) -> list:
        return self.data.get("notes", [])

    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self.provider["id"]

    @property
    def display_name(self) -> str:
        return self.provider["display_name"]

    @property
    def vendor(self) -> str:
        return self.provider["vendor"]

    @property
    def base_url(self) -> str:
        return self.base_urls["native"]

    @property
    def openai_base_url(self) -> str:
        return self.base_urls["openai"]

    @property
    def default_model(self) -> str:
        return self.testing["default_model"]

    @property
    def api_key_env(self) -> str:
        return self.authentication["environment_variable"]