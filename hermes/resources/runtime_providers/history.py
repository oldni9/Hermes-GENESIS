"""
===============================================================================
Hermes Runtime Provider History

Persistent provider history.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict


class ProviderHistory:

    def __init__(self) -> None:

        self._history = defaultdict(list)

    # --------------------------------------------------------------

    def append(
        self,
        provider: str,
        record: dict,
    ) -> None:

        self._history[provider].append(record)

    # --------------------------------------------------------------

    def records(
        self,
        provider: str,
    ) -> list[dict]:

        return list(self._history[provider])

    # --------------------------------------------------------------

    def clear(
        self,
        provider: str | None = None,
    ) -> None:

        if provider is None:

            self._history.clear()

            return

        self._history.pop(provider, None)
