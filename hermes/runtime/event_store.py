"""
===============================================================================
Execution Event Store
===============================================================================

Sprint 17A.5 Final Freeze:
- Uses RuntimeSerializer for deserialization.
- Silently skips SerializationError during replay to prevent crashing WS.
- Added serialization_failures metric and logging for skipped corrupt events.
- Enriched corruption logging with execution_id context.
===============================================================================
"""
from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from typing import Dict, List, Tuple

from hermes.runtime.events.base import BaseEvent
from hermes.runtime.serializer import RuntimeSerializer, SerializationError

logger = logging.getLogger(__name__)


class ExecutionEventStore:
    """Thread-safe bounded ring buffer for storing recent execution events."""
    
    def __init__(self, max_events: int = 500, max_chars: int = 500_000) -> None:
        self._events: Dict[str, deque] = defaultdict(deque)
        self._sizes: Dict[str, int] = defaultdict(int)
        self._seq_counters: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._max_events = max_events
        self._max_chars = max_chars
        self.replay_hits: int = 0
        self.replay_misses: int = 0
        self.serialization_failures: int = 0

    def append(self, event: BaseEvent) -> None:
        """Appends an event, assigns a sequence number, and trims the buffer."""
        with self._lock:
            seq = self._seq_counters[event.execution_id] + 1
            self._seq_counters[event.execution_id] = seq
            event.sequence = seq
            
            json_str = RuntimeSerializer.serialize(event)
            size = len(json_str)
            
            self._events[event.execution_id].append(json_str)
            self._sizes[event.execution_id] += size
            
            # Trim if exceeding limits
            while self._sizes[event.execution_id] > self._max_chars or len(self._events[event.execution_id]) > self._max_events:
                if not self._events[event.execution_id]:
                    break
                old = self._events[event.execution_id].popleft()
                self._sizes[event.execution_id] -= len(old)

    def replay_and_get_last_seq(self, execution_id: str, last_sequence: int = 0) -> Tuple[List[BaseEvent], int, int]:
        """
        Returns (events, last_seq, oldest_seq).
        - events: List of events with sequence > last_sequence.
        - last_seq: The highest sequence number observed.
        - oldest_seq: The lowest sequence number currently in the buffer.
        """
        with self._lock:
            if execution_id not in self._events or not self._events[execution_id]:
                return [], 0, 0
                
            last_seq = self._seq_counters.get(execution_id, 0)
            
            # Determine oldest sequence in the buffer
            oldest_seq = 0
            try:
                first_event = RuntimeSerializer.deserialize(self._events[execution_id][0])
                oldest_seq = first_event.sequence
            except SerializationError as e:
                self.serialization_failures += 1
                logger.warning(
                    "Skipping corrupt runtime event in replay buffer for execution %s: %s", 
                    execution_id, str(e)
                )
            
            events = []
            hit = False
            for json_str in list(self._events[execution_id]):
                try:
                    event = RuntimeSerializer.deserialize(json_str)
                    if event.sequence > last_sequence:
                        events.append(event)
                        hit = True
                except SerializationError as e:
                    self.serialization_failures += 1
                    logger.warning(
                        "Skipping corrupt runtime event during replay for execution %s: %s", 
                        execution_id, str(e)
                    )
                    continue
                    
            if hit:
                self.replay_hits += 1
            elif last_sequence > 0 and last_seq > last_sequence:
                self.replay_misses += 1
                
            return events, last_seq, oldest_seq

    def get_last_sequence(self, execution_id: str) -> int:
        """Returns the highest sequence number for an execution."""
        with self._lock:
            return self._seq_counters.get(execution_id, 0)

    def clear(self, execution_id: str) -> None:
        """Clears the event store for a specific execution."""
        with self._lock:
            if execution_id in self._events:
                del self._events[execution_id]
                del self._sizes[execution_id]
                del self._seq_counters[execution_id]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture