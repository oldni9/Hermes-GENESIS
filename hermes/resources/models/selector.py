"""
===============================================================================
Hermes Runtime Model Selector

Chooses candidate Runtime Models before scoring.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Iterable

from hermes.resources.models.model import RuntimeModel
from hermes.resources.models.registry import ModelRegistry


class ModelSelector:
    """
    Selects candidate models from the registry.

    This class does NOT rank models.

    It simply filters models that satisfy
    execution requirements.

    Ranking belongs to ScoreEngine later.
    """

    def __init__(
        self,
        registry: ModelRegistry,
    ) -> None:

        self._registry = registry

    # ------------------------------------------------------------------

    def all(self) -> list[RuntimeModel]:
        """
        Return every enabled model.
        """

        return [model for model in self._registry.all() if model.enabled]

    # ------------------------------------------------------------------

    def by_provider(
        self,
        provider: str,
    ) -> list[RuntimeModel]:
        """
        Return enabled models belonging
        to one provider.
        """

        return [model for model in self.all() if model.provider == provider]

    # ------------------------------------------------------------------

    def by_capability(
        self,
        capability: str,
    ) -> list[RuntimeModel]:
        """
        Return models supporting
        a capability.
        """

        return [model for model in self.all() if capability in model.capabilities]

    # ------------------------------------------------------------------

    def filter(
        self,
        models: Iterable[RuntimeModel],
    ) -> list[RuntimeModel]:
        """
        Remove disabled models.
        """

        return [model for model in models if model.enabled]
