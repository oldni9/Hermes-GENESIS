"""
===============================================================================
Tests for Runtime Serializer (Sprint 17A.5)
===============================================================================
"""
import pytest
import json
from uuid import uuid4

from hermes.runtime.events.base import BaseEvent, SCHEMA_VERSION
from hermes.runtime.events.execution import ExecutionStartedEvent, ExecutionFinishedEvent
from hermes.runtime.events.system import ReplayGapEvent, ReplayGapPayload
from hermes.runtime.serializer import RuntimeSerializer, SerializationError


def test_serialize_base_event():
    event = BaseEvent(event_type="test", execution_id="exec-123")
    json_str = RuntimeSerializer.serialize(event)
    assert isinstance(json_str, str)
    assert '"event_type":"test"' in json_str
    assert '"execution_id":"exec-123"' in json_str
    assert f'"schema_version":"{SCHEMA_VERSION}"' in json_str

def test_deserialize_execution_started():
    original = ExecutionStartedEvent(execution_id="exec-123", payload={"prompt": "Hello"})
    json_str = RuntimeSerializer.serialize(original)
    
    deserialized = RuntimeSerializer.deserialize(json_str)
    
    assert isinstance(deserialized, ExecutionStartedEvent)
    assert deserialized.execution_id == "exec-123"
    assert deserialized.payload == {"prompt": "Hello"}

def test_deserialize_execution_finished():
    original = ExecutionFinishedEvent(execution_id="exec-123", payload={"result": "Done"})
    json_str = RuntimeSerializer.serialize(original)
    
    deserialized = RuntimeSerializer.deserialize(json_str)
    
    assert isinstance(deserialized, ExecutionFinishedEvent)
    assert deserialized.payload["result"] == "Done"

def test_deserializer_uses_registry():
    """Ensure that known event types with different payloads map to the correct class."""
    start_event = ExecutionStartedEvent(execution_id="exec-1")
    finish_event = ExecutionFinishedEvent(execution_id="exec-1")
    
    start_json = RuntimeSerializer.serialize(start_event)
    finish_json = RuntimeSerializer.serialize(finish_event)
    
    deserialized_start = RuntimeSerializer.deserialize(start_json)
    deserialized_finish = RuntimeSerializer.deserialize(finish_json)
    
    assert isinstance(deserialized_start, ExecutionStartedEvent)
    assert not isinstance(deserialized_start, ExecutionFinishedEvent)
    
    assert isinstance(deserialized_finish, ExecutionFinishedEvent)
    assert not isinstance(deserialized_finish, ExecutionStartedEvent)

def test_deserialize_replay_gap_event():
    payload = ReplayGapPayload(
        requested_sequence=10,
        oldest_available_sequence=20,
        latest_available_sequence=50,
        missing_event_count=9
    )
    original = ReplayGapEvent(execution_id="exec-123", payload=payload)
    json_str = RuntimeSerializer.serialize(original)
    
    deserialized = RuntimeSerializer.deserialize(json_str)
    
    assert isinstance(deserialized, ReplayGapEvent)
    assert isinstance(deserialized.payload, ReplayGapPayload)
    # Enforce typed property access, not dict indexing
    assert deserialized.payload.requested_sequence == 10
    assert deserialized.payload.missing_event_count == 9

def test_deserialize_unknown_event_type_raises_error():
    json_str = '{"event_type":"unknown_event","execution_id":"exec-123","timestamp":123.456,"schema_version":"1.0.0","sequence":1,"payload":{}}'
    
    with pytest.raises(SerializationError, match="Unknown event_type 'unknown_event'"):
        RuntimeSerializer.deserialize(json_str)

def test_deserialize_missing_event_type_raises_error():
    json_str = '{"execution_id":"exec-123","timestamp":123.456,"schema_version":"1.0.0","sequence":1,"payload":{}}'
    
    with pytest.raises(SerializationError, match="Missing 'event_type'"):
        RuntimeSerializer.deserialize(json_str)

def test_deserialize_malformed_json_raises_error():
    json_str = '{"event_type":"execution_started", "execution_id": "exec-123"'
    
    with pytest.raises(SerializationError, match="Invalid JSON"):
        RuntimeSerializer.deserialize(json_str)

def test_deserialize_validation_error_raises_serialization_error():
    # Missing required execution_id field
    json_str = '{"event_type":"execution_started","timestamp":123.456,"schema_version":"1.0.0","sequence":1,"payload":{}}'
    
    with pytest.raises(SerializationError, match="Failed to validate execution_started"):
        RuntimeSerializer.deserialize(json_str)

def test_unknown_schema_version_raises_error():
    json_str = '{"event_type":"execution_started","execution_id":"exec-123","timestamp":123.456,"schema_version":"9.9.9","sequence":1,"payload":{}}'
    
    with pytest.raises(SerializationError, match="Unsupported schema_version '9.9.9'"):
        RuntimeSerializer.deserialize(json_str)

def test_round_trip_all_event_types():
    events = [
        ExecutionStartedEvent(execution_id="exec-1"),
        ExecutionFinishedEvent(execution_id="exec-1"),
        ReplayGapEvent(
            execution_id="exec-1",
            payload=ReplayGapPayload(
                requested_sequence=1,
                oldest_available_sequence=2,
                latest_available_sequence=3,
                missing_event_count=0
            )
        )
    ]
    
    for event in events:
        json_str = RuntimeSerializer.serialize(event)
        deserialized = RuntimeSerializer.deserialize(json_str)
        assert type(deserialized) == type(event)
        # UUID round-trip check
        assert deserialized.event_id == event.event_id
        assert isinstance(deserialized.event_id, type(event.event_id))
        assert deserialized.execution_id == event.execution_id