"""
===============================================================================
Hermes Event Registry
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict

from hermes.events.subscriber import EventSubscriber


class EventRegistry:

    def __init__(self):

        self._subs = defaultdict(list)

    def subscribe(

        self,

        event: str,

        subscriber: EventSubscriber,

    ):

        self._subs[event].append(subscriber)

    def subscribers(

        self,

        event: str,

    ):

        return list(self._subs[event])