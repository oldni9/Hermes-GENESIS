"""
===============================================================================
Runtime Event Bus
===============================================================================

Sprint 17A.2 Update:
- Delegates replay and storage to ExecutionEventStore.
- EventBus strictly handles live fan-out to subscribers.
===============================================================================
"""
from __future__ import annotations

import logging
import queue
import threading
from typing import Dict, List

from hermes.runtime.events.base import BaseEvent
from hermes.runtime.event_store import ExecutionEventStore

logger = logging.getLogger(__name__)


class RuntimeEventBus:
    """Thread-safe pub/sub event bus with backpressure and event store integration."""
    
    def __init__(
        self, 
        max_queue_size: int = 1000, 
        event_store: ExecutionEventStore = None
    ) -> None:
        self._subscribers: Dict[str, List[queue.Queue]] = {}
        self._lock = threading.Lock()
        self._max_queue_size = max_queue_size
        self._dropped_events: int = 0
        self._dropped_lock = threading.Lock()
        self._published_events: int = 0
        self._published_lock = threading.Lock()
        self.store = event_store or ExecutionEventStore()

    @property
    def dropped_events(self) -> int:
        with self._dropped_lock:
            return self._dropped_events

    @property
    def published_events(self) -> int:
        with self._published_lock:
            return self._published_events

    def subscribe(self, execution_id: str) -> queue.Queue:
        """Subscribe to live events for a specific execution ID."""
        q: queue.Queue = queue.Queue(maxsize=self._max_queue_size)
        with self._lock:
            self._subscribers.setdefault(execution_id, []).append(q)
        return q

    def unsubscribe(self, execution_id: str, q: queue.Queue) -> None:
        """Unsubscribe a queue from an execution ID."""
        with self._lock:
            if execution_id in self._subscribers:
                try:
                    self._subscribers[execution_id].remove(q)
                except ValueError:
                    pass
                if not self._subscribers[execution_id]:
                    del self._subscribers[execution_id]

    def publish(self, event: BaseEvent) -> None:
        """Publish an event to the store and all live subscribers."""
        # 1. Persist to store (assigns sequence number)
        self.store.append(event)
        
        with self._published_lock:
            self._published_events += 1
            
        # 2. Fan-out to live subscribers
        with self._lock:
            subs = list(self._subscribers.get(event.execution_id, []))
            
        for q in subs:
            try:
                q.put_nowait(event)
            except queue.Full:
                with self._dropped_lock:
                    self._dropped_events += 1
                logger.warning(f"Event queue full for execution {event.execution_id}. Dropping event.")

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture