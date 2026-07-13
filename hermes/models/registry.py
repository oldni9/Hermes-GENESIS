"""
===============================================================================
Hermes Model Registry
===============================================================================
"""

from hermes.models.enums import ModelType
from hermes.models.model import Model


class ModelRegistry:

    def __init__(self):

        self._models: dict[
            ModelType,
            Model,
        ] = {}

    def register(
        self,
        model: Model,
    ):

        self._models[
            model.name
        ] = model

    def get(
        self,
        model: ModelType,
    ):

        return self._models.get(
            model,
        )

    def all(
        self,
    ):

        return list(
            self._models.values()
        )