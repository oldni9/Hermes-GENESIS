"""
===============================================================================
Hermes Runtime Model History

Persistent execution history.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict


class ModelHistory:
    """
    Stores long-term execution history.

    Unlike Telemetry, this survives
    across Hermes sessions.
    """

    def __init__(self) -> None:

        self._history = defaultdict(list)

    # ------------------------------------------------------------------

    def append(
        self,
        model: str,
        record: dict,
    ) -> None:

        self._history[model].append(record)

    # ------------------------------------------------------------------

    def records(
        self,
        model: str,
    ) -> list[dict]:

        return list(self._history[model])

    # ------------------------------------------------------------------

    def clear(
        self,
        model: str | None = None,
    ) -> None:

        if model is None:

            self._history.clear()

            return

        self._history.pop(model, None)