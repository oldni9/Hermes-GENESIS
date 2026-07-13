"""
===============================================================================
Hermes Runtime Provider Selector

Selects Providers for execution.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.providers.provider import RuntimeProvider


class RuntimeProviderSelector:

    def select(
        self,
        providers: list[RuntimeProvider],
    ) -> RuntimeProvider | None:

        if not providers:
            return None

        providers.sort(
            key=lambda provider: provider.priority,
            reverse=True,
        )

        return providers[0]