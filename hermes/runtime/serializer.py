"""
===============================================================================
Runtime Serializer
===============================================================================

Sprint 17A.5 Final Freeze:
- Frozen EVENT_REGISTRY using MappingProxyType to prevent runtime mutation.
- Validates schema_version strictly against the centralized constant.
- Narrowed exception handling to only catch expected parsing errors.
===============================================================================
"""
from __future__ import annotations

import json
from types import MappingProxyType
from typing import Type

from pydantic import ValidationError

from hermes.runtime.events.base import BaseEvent, SCHEMA_VERSION
from hermes.runtime.events.cancellation import CancellationRequestedEvent, ExecutionCancelledEvent
from hermes.runtime.events.execution import ExecutionFailedEvent, ExecutionFinishedEvent, ExecutionStartedEvent
from hermes.runtime.events.system import ReplayGapEvent
from hermes.runtime.events.trace import TraceRuntimeEvent


class SerializationError(Exception):
    """Raised when an event cannot be deserialized correctly."""
    pass


# Discriminator registry for safe deserialization (Single Source of Truth)
# Wrapped in MappingProxyType to make it immutable at runtime (v1.0.0 Freeze)
_EVENT_REGISTRY_IMPL: dict[str, Type[BaseEvent]] = {
    "execution_started": ExecutionStartedEvent,
    "execution_finished": ExecutionFinishedEvent,
    "execution_failed": ExecutionFailedEvent,
    "trace": TraceRuntimeEvent,
    "cancellation_requested": CancellationRequestedEvent,
    "execution_cancelled": ExecutionCancelledEvent,
    "replay_gap": ReplayGapEvent,
}
EVENT_REGISTRY = MappingProxyType(_EVENT_REGISTRY_IMPL)


class RuntimeSerializer:
    """Centralized serialization/deserialization for runtime events."""
    
    @staticmethod
    def serialize(event: BaseEvent) -> str:
        """Serializes a BaseEvent to a JSON string."""
        return event.model_dump_json()
        
    @staticmethod
    def deserialize(json_str: str) -> BaseEvent:
        """
        Deserializes a JSON string back into the correct BaseEvent subclass.
        Raises SerializationError for unknown event types, malformed JSON, 
        validation failures, or unsupported schema versions.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {e}") from e
            
        # Strict Schema Version Validation
        version = data.get("schema_version")
        if version != SCHEMA_VERSION:
            raise SerializationError(f"Unsupported schema_version '{version}'. Expected '{SCHEMA_VERSION}'.")
            
        event_type = data.get("event_type")
        if not event_type:
            raise SerializationError(f"Missing 'event_type' in JSON: {json_str}")
            
        event_cls = EVENT_REGISTRY.get(event_type)
        if not event_cls:
            raise SerializationError(f"Unknown event_type '{event_type}'")
            
        try:
            return event_cls.model_validate(data)
        except ValidationError as e:
            raise SerializationError(f"Failed to validate {event_type}: {e}") from e

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture