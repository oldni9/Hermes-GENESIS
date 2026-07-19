"""
===============================================================================
Hermes Event History
===============================================================================
"""

from __future__ import annotations

from collections import deque

from hermes.events.event import Event


class EventHistory:
    """
    Keeps the most recent runtime events.

    Old events are discarded automatically.
    """

    def __init__(
        self,
        max_events: int = 1000,
    ):

        self._events = deque(maxlen=max_events)

    # ---------------------------------------------------------

    def add(
        self,
        event: Event,
    ) -> None:

        self._events.append(event)

    # ---------------------------------------------------------

    def all(self):

        return list(self._events)

    # ---------------------------------------------------------

    def latest(
        self,
        count: int = 10,
    ):

        return list(self._events)[-count:]

    # ---------------------------------------------------------

    def clear(self):

        self._events.clear()

    # ---------------------------------------------------------

    def count(self):

        return len(self._events)
