"""
===============================================================================
Hermes Model Registry
===============================================================================
"""

from __future__ import annotations

from .exceptions import ModelAlreadyExists
from .model import RuntimeModel


class ModelRegistry:

    def __init__(self) -> None:

        self._models: dict[str, RuntimeModel] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        model: RuntimeModel,
    ) -> None:

        if model.id in self._models:

            raise ModelAlreadyExists(
                f"Model '{model.id}' already exists."
            )

        self._models[model.id] = model

    # ------------------------------------------------------------------

    def unregister(
        self,
        model_id: str,
    ) -> None:

        self._models.pop(model_id, None)

    # ------------------------------------------------------------------

    def get(
        self,
        model_id: str,
    ) -> RuntimeModel | None:

        return self._models.get(model_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeModel]:

        return list(self._models.values())

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeModel]:

        return [

            model

            for model in self._models.values()

            if model.enabled

        ]

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._models.clear()