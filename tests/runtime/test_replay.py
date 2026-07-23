"""
===============================================================================
Tests for Replay and ReplayGapEvent (Sprint 17A.5)
===============================================================================
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from hermes.runtime.event_store import ExecutionEventStore
from hermes.runtime.events.execution import ExecutionStartedEvent, ExecutionFinishedEvent
from hermes.runtime.events.system import ReplayGapEvent, ReplayGapPayload
from hermes.runtime.serializer import RuntimeSerializer


@pytest.fixture
def store():
    return ExecutionEventStore(max_events=5, max_chars=100_000)

def test_replay_returns_events_after_sequence(store):
    exec_id = "exec-1"
    
    # Append 3 valid, registered events
    for i in range(3):
        event = ExecutionStartedEvent(execution_id=exec_id)
        store.append(event)
        
    # Request events after sequence 1
    events, last_seq, oldest_seq = store.replay_and_get_last_seq(exec_id, last_sequence=1)
    
    assert len(events) == 2
    assert events[0].sequence == 2
    assert events[1].sequence == 3
    assert last_seq == 3
    assert oldest_seq == 1

def test_replay_returns_empty_if_no_new_events(store):
    exec_id = "exec-1"
    
    # Append 1 valid event
    event = ExecutionStartedEvent(execution_id=exec_id)
    store.append(event)
        
    # Request events after sequence 5 (none exist)
    events, last_seq, oldest_seq = store.replay_and_get_last_seq(exec_id, last_sequence=5)
    
    assert len(events) == 0
    assert last_seq == 1
    assert oldest_seq == 1

def test_replay_detects_gap(store):
    exec_id = "exec-1"
    
    # Append 10 events, but buffer only holds 5
    for i in range(10):
        event = ExecutionStartedEvent(execution_id=exec_id)
        store.append(event)
        
    # Request events after sequence 2 (buffer has sequences 6-10)
    events, last_seq, oldest_seq = store.replay_and_get_last_seq(exec_id, last_sequence=2)
    
    # Should only return events 6-10
    assert len(events) == 5
    assert events[0].sequence == 6
    assert last_seq == 10
    assert oldest_seq == 6

def test_replay_gap_integration_with_mock_websocket():
    """Integration test simulating the WebSocket layer's check using the store."""
    exec_id = "exec-1"
    store = ExecutionEventStore(max_events=5)
    
    for i in range(10):
        event = ExecutionStartedEvent(execution_id=exec_id)
        store.append(event)
        
    last_sequence = 2
    events, last_seq, oldest_seq = store.replay_and_get_last_seq(exec_id, last_sequence)
    
    gap_event = None
    # Simulate the WebSocket layer's check
    if last_sequence > 0 and last_sequence < oldest_seq:
        missing_count = oldest_seq - last_sequence - 1
        # Explicitly construct payload
        gap_payload = ReplayGapPayload(
            requested_sequence=last_sequence,
            oldest_available_sequence=oldest_seq,
            latest_available_sequence=last_seq,
            missing_event_count=missing_count
        )
        gap_event = ReplayGapEvent(
            execution_id=exec_id,
            payload=gap_payload
        )
        
    assert gap_event is not None
    assert gap_event.event_type == "replay_gap"
    
    # Serialize and deserialize to ensure it survives the wire
    json_str = gap_event.model_dump_json()
    deserialized = RuntimeSerializer.deserialize(json_str)
    
    assert isinstance(deserialized, ReplayGapEvent)
    assert deserialized.payload.requested_sequence == 2
    assert deserialized.payload.oldest_available_sequence == 6
    assert deserialized.payload.latest_available_sequence == 10
    assert deserialized.payload.missing_event_count == 3  # seqs 3, 4, 5 are missing

def test_corrupt_event_skipped_during_replay():
    exec_id = "exec-1"
    store = ExecutionEventStore()
    
    # Append 2 valid events
    store.append(ExecutionStartedEvent(execution_id=exec_id))
    store.append(ExecutionFinishedEvent(execution_id=exec_id))
    
    # Manually inject a corrupt JSON string (missing schema_version) into the buffer
    with store._lock:
        store._events[exec_id].append('{"event_type":"execution_started","execution_id":"exec-1"}')
        store._sizes[exec_id] += 50
        
    # Append 1 more valid event
    store.append(ExecutionStartedEvent(execution_id=exec_id))
    
    # Replay should skip the corrupt event and return the 3 valid ones
    events, last_seq, oldest_seq = store.replay_and_get_last_seq(exec_id, 0)
    
    assert len(events) == 3
    assert store.serialization_failures == 1