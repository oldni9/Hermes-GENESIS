"""
===============================================================================
Hermes Runtime Model Filters

Reusable filters for Runtime Models.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Iterable

from hermes.resources.models.model import RuntimeModel


class ModelFilters:
    """
    Collection of reusable RuntimeModel filters.
    """

    @staticmethod
    def enabled(
        models: Iterable[RuntimeModel],
    ) -> list[RuntimeModel]:

        return [model for model in models if model.enabled]

    # ------------------------------------------------------------------

    @staticmethod
    def provider(
        models: Iterable[RuntimeModel],
        provider: str,
    ) -> list[RuntimeModel]:

        return [model for model in models if model.provider == provider]

    # ------------------------------------------------------------------

    @staticmethod
    def capability(
        models: Iterable[RuntimeModel],
        capability: str,
    ) -> list[RuntimeModel]:

        return [model for model in models if capability in model.capabilities]

    # ------------------------------------------------------------------

    @staticmethod
    def minimum_context(
        models: Iterable[RuntimeModel],
        tokens: int,
    ) -> list[RuntimeModel]:

        return [model for model in models if model.context_window >= tokens]
