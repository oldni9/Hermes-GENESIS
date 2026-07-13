"""
===============================================================================
Hermes Runtime Model Manager
===============================================================================

High-level manager for Runtime Models.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .loader import ModelLoader
from .model import RuntimeModel
from .registry import ModelRegistry
from .validator import ModelValidator


class ModelManager:
    """
    Coordinates Runtime Models.
    """

    def __init__(self) -> None:

        self._registry = ModelRegistry()

        self._validator = ModelValidator()

        self._loader = ModelLoader()

    # ------------------------------------------------------------------

    def register(
        self,
        model: RuntimeModel,
    ) -> None:

        self._validator.validate(model)

        self._registry.register(model)

    # ------------------------------------------------------------------

    def discover(
        self,
        directory: Path,
    ) -> None:

        models = self._loader.load(directory)

        for model in models:

            self.register(model)

    # ------------------------------------------------------------------

    def get(
        self,
        model_id: str,
    ) -> RuntimeModel | None:

        return self._registry.get(model_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeModel]:

        return self._registry.all()

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeModel]:

        return self._registry.enabled()

    # ------------------------------------------------------------------

    def unregister(
        self,
        model_id: str,
    ) -> None:

        self._registry.unregister(model_id)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._registry.clear()