"""
===============================================================================
Hermes Event Registry
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict

from hermes.events.subscriber import EventSubscriber


class EventRegistry:
    """
    Store event subscribers by event name.

    The registry owns subscription state only. Event dispatch remains the
    responsibility of :class:`EventBus`.
    """

    def __init__(self) -> None:

        self._subscribers: defaultdict[str, list[EventSubscriber]] = defaultdict(list)

    def subscribe(

        self,

        event: str,

        subscriber: EventSubscriber,

    ) -> None:

        subscribers = self._subscribers[event]

        if any(registered is subscriber for registered in subscribers):
            return

        subscribers.append(subscriber)

    def unsubscribe(

        self,

        event: str,

        subscriber: EventSubscriber,

    ) -> None:

        subscribers = self._subscribers.get(event)

        if subscribers is None:
            return

        for registered in subscribers:
            if registered is subscriber:
                subscribers.remove(registered)
                break

        if not subscribers:
            del self._subscribers[event]

    def subscribers(

        self,

        event: str,

    ) -> list[EventSubscriber]:

        return list(self._subscribers.get(event, ()))

    def clear(self) -> None:

        self._subscribers.clear()
