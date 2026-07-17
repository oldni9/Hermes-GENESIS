"""
===============================================================================
Tests for Hermes Event System

Validates EventBus behavior: subscription, unsubscription, history, clearing.

No external dependencies.
All tests are deterministic.
===============================================================================
"""

from __future__ import annotations

import unittest

from hermes.events.bus import EventBus
from hermes.events.event import Event
from hermes.events.subscriber import EventSubscriber


class RecordingSubscriber(EventSubscriber):
    """Subscriber that records all events it receives."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


class TestEventBus(unittest.TestCase):
    """Test suite for EventBus."""

    def setUp(self) -> None:
        self.bus = EventBus()
        self.subscriber = RecordingSubscriber()

    def test_subscribe_and_publish_delivers_event(self) -> None:
        """Subscribed subscriber receives published event."""
        event = Event(name="test", source="test_source", data={"key": "value"})
        self.bus.subscribe("test", self.subscriber)
        self.bus.publish(event)
        self.assertEqual([event], self.subscriber.events)

    def test_unsubscribe_stops_future_notifications(self) -> None:
        """Unsubscribed subscriber does not receive subsequent events."""
        event1 = Event(name="test", source="source1")
        event2 = Event(name="test", source="source2")

        self.bus.subscribe("test", self.subscriber)
        self.bus.publish(event1)
        self.assertEqual([event1], self.subscriber.events)

        self.bus.unsubscribe("test", self.subscriber)
        self.bus.publish(event2)
        self.assertEqual([event1], self.subscriber.events)  # No new event appended

    def test_history_preserves_every_published_event_in_order(self) -> None:
        """Event history stores all events in publishing order."""
        event1 = Event(name="one", source="a")
        event2 = Event(name="two", source="b")
        event3 = Event(name="three", source="c")

        self.bus.publish(event1)
        self.bus.publish(event2)
        self.bus.publish(event3)

        history = self.bus.history.all()
        self.assertEqual([event1, event2, event3], history)

    def test_clear_removes_subscriptions_and_history(self) -> None:
        """clear() empties history and removes all subscribers."""
        event1 = Event(name="test", source="s1")
        event2 = Event(name="test", source="s2")

        self.bus.subscribe("test", self.subscriber)
        self.bus.publish(event1)
        self.assertEqual([event1], self.subscriber.events)
        self.assertEqual(1, self.bus.history.count())

        self.bus.clear()
        self.assertEqual(0, self.bus.history.count())
        self.assertEqual(0, self.bus.subscriber_count("test"))

        # After clear, publishing a new event should create new history but
        # no subscriber receives it because they were cleared.
        self.bus.publish(event2)
        self.assertEqual([event1], self.subscriber.events)  # No new event
        self.assertEqual([event2], self.bus.history.all())  # History contains only the new event


if __name__ == "__main__":
    unittest.main()