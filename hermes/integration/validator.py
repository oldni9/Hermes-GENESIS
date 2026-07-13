"""
===============================================================================
Hermes Integration Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.integration.context import IntegrationContext


class IntegrationValidator:

    def validate(
        self,
        context: IntegrationContext,
    ) -> None:

        if not context.prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )