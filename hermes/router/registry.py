"""
===============================================================================
Model Registry
===============================================================================
"""

from __future__ import annotations

from hermes.models.model import Model


class ModelRegistry:

    def __init__(self) -> None:

        self._models: dict[str, Model] = {}

    def register(
        self,
        model: Model,
    ) -> None:

        self._models[model.name] = model

    def get(
        self,
        name: str,
    ) -> Model:

        return self._models[name]

    def all(
        self,
    ) -> list[Model]:

        return list(self._models.values())
