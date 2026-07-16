"""
===============================================================================
Hermes Event Bus

Central publish / subscribe system for Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.events.event import Event
from hermes.events.history import EventHistory
from hermes.events.logger import EventLogger
from hermes.events.registry import EventRegistry
from hermes.events.subscriber import EventSubscriber


class EventBus:
    """
    Central event dispatcher.

    Responsibilities
    ----------------
    • Maintain subscriber registry
    • Publish events
    • Keep recent event history
    • Log every event
    """

    def __init__(self) -> None:

        self._registry = EventRegistry()

        self._history = EventHistory()

        self._logger = EventLogger()

    # ------------------------------------------------------------------

    @property
    def history(self) -> EventHistory:

        return self._history

    # ------------------------------------------------------------------

    @property
    def registry(self) -> EventRegistry:

        return self._registry

    # ------------------------------------------------------------------

    def subscribe(

        self,

        event_name: str,

        subscriber: EventSubscriber,

    ) -> None:

        self._registry.subscribe(

            event_name,

            subscriber,

        )

    # ------------------------------------------------------------------

    def unsubscribe(

        self,

        event_name: str,

        subscriber: EventSubscriber,

    ) -> None:

        self._registry.unsubscribe(

            event_name,

            subscriber,

        )

    # ------------------------------------------------------------------

    def publish(

        self,

        event: Event,

    ) -> None:

        self._history.add(event)

        self._logger.log(event)

        subscribers = self._registry.subscribers(event.name)

        for subscriber in subscribers:

            subscriber.notify(event)

    # ------------------------------------------------------------------

    def clear(self) -> None:

        self._history.clear()

        self._registry.clear()

    # ------------------------------------------------------------------

    def subscriber_count(

        self,

        event_name: str,

    ) -> int:

        return len(

            self._registry.subscribers(

                event_name,

            )

        )