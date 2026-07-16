"""
===============================================================================
Hermes Event Subscriber
===============================================================================
"""

from __future__ import annotations

from abc import ABC

from abc import abstractmethod

from hermes.events.event import Event


class EventSubscriber(ABC):

    @abstractmethod

    def notify(

        self,

        event: Event,

    ) -> None:

        ...