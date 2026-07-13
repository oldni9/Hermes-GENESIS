"""
===============================================================================
Hermes Runtime Resource Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.exceptions import (
    ResourceValidationError,
)


class RuntimeResourceValidator:
    """
    Validates runtime resources.
    """

    def validate(
        self,
        resource: dict,
    ) -> None:

        if "name" not in resource:

            raise ResourceValidationError(
                "Runtime resource requires a name."
            )

        if "enabled" not in resource:

            raise ResourceValidationError(
                f"{resource['name']} missing 'enabled'."
            )