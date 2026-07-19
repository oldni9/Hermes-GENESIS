"""
===============================================================================
Hermes Runtime Model Validator
===============================================================================
"""

from __future__ import annotations

from .exceptions import InvalidModel
from .model import RuntimeModel


class ModelValidator:
    """
    Validates RuntimeModel objects.
    """

    def validate(
        self,
        model: RuntimeModel,
    ) -> None:

        if not model.id.strip():

            raise InvalidModel("Model id cannot be empty.")

        if not model.provider.strip():

            raise InvalidModel("Provider cannot be empty.")

        if not model.model.strip():

            raise InvalidModel("Provider model id cannot be empty.")

        if model.priority < 0:

            raise InvalidModel("Priority cannot be negative.")

        if model.context_window <= 0:

            raise InvalidModel("Context window must be positive.")
