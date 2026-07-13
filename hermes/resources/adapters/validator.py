"""
===============================================================================
Hermes Adapter Validator
===============================================================================

Validates Runtime Adapter Objects before they are registered.

===============================================================================
"""

from __future__ import annotations

from .adapter import RuntimeAdapter
from .exceptions import AdapterValidationError


class AdapterValidator:
    """
    Validates Runtime Adapters.
    """

    REQUIRED_TYPES = {
        "llm",
        "embedding",
        "vision",
        "speech",
        "custom",
    }

    # ------------------------------------------------------------------

    def validate(
        self,
        adapter: RuntimeAdapter,
    ) -> None:
        """
        Validate an adapter.
        """

        if not adapter.id.strip():

            raise AdapterValidationError(
                "Adapter id cannot be empty."
            )

        if not adapter.name.strip():

            raise AdapterValidationError(
                "Adapter name cannot be empty."
            )

        if adapter.adapter_type not in self.REQUIRED_TYPES:

            raise AdapterValidationError(
                f"Unsupported adapter type '{adapter.adapter_type}'."
            )

        if adapter.priority < 0:

            raise AdapterValidationError(
                "Priority cannot be negative."
            )