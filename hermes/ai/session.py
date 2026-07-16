"""
===============================================================================
Hermes AI Session Engine

Canonical AI Session manager for Hermes.

A session manages the entire lifecycle of an AI interaction.

Features:
    - Unique session ID
    - State management (CREATED → READY → RUNNING → STREAMING → COMPLETED/FAILED/CANCELLED/CLOSED)
    - Request/Response/Prompt history
    - Statistics and event logging
    - Metadata and tags
    - Streaming support (chunk accumulation)
    - Serialization (dict/JSON)
    - Context manager support
    - Cloning and resetting

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generator, Iterable, Self

from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ResponseChunk
from hermes.ai.prompt import Prompt


# =============================================================================
# Session State
# =============================================================================

class SessionState(str, Enum):
    """
    States of an AISession.

    CREATED   - Session initialized but not ready
    READY     - Ready to accept requests
    RUNNING   - Actively processing a request
    STREAMING - Streaming a response
    COMPLETED - Successfully finished
    FAILED    - Failed with an error
    CANCELLED - Cancelled by user
    CLOSED    - Closed (no further operations)
    """

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


# =============================================================================
# Session Event
# =============================================================================

@dataclass(slots=True)
class SessionEvent:
    """
    An event recorded during the session lifecycle.

    Attributes
    ----------
    type : str
        Event type (e.g., "request_start", "response_received", "error").
    timestamp : float
        Unix timestamp when the event occurred.
    data : dict[str, Any] | None
        Additional event data.
    source : str | None
        Source of the event (e.g., "user", "system", "provider").
    """

    type: str
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result = {
            "type": self.type,
            "timestamp": self.timestamp,
        }
        if self.data is not None:
            result["data"] = self.data
        if self.source is not None:
            result["source"] = self.source
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionEvent:
        """Create from a dictionary."""
        return cls(
            type=data["type"],
            timestamp=data.get("timestamp", time.time()),
            data=data.get("data"),
            source=data.get("source"),
        )


# =============================================================================
# Session Statistics
# =============================================================================

@dataclass(slots=True)
class SessionStatistics:
    """
    Statistics collected during the session.

    Attributes
    ----------
    request_count : int
        Number of requests sent.
    response_count : int
        Number of responses received.
    token_prompt_total : int
        Total prompt tokens across all requests.
    token_completion_total : int
        Total completion tokens across all responses.
    token_total : int
        Total tokens (prompt + completion).
    duration_total : float
        Total time spent processing (sum of individual response durations).
    first_token_time : float | None
        Time to first token in streaming (if applicable).
    last_response_time : float | None
        Timestamp of the last response.
    created_at : datetime
        When statistics were computed.
    """

    request_count: int = 0
    response_count: int = 0
    token_prompt_total: int = 0
    token_completion_total: int = 0
    token_total: int = 0
    duration_total: float = 0.0
    first_token_time: float | None = None
    last_response_time: float | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def update_with_response(self, response: AIResponse) -> None:
        """
        Update statistics with a new AIResponse.

        Parameters
        ----------
        response : AIResponse
            The response to incorporate.
        """
        self.response_count += 1
        if response.duration:
            self.duration_total += response.duration
        if response.usage:
            self.token_prompt_total += response.usage.prompt_tokens
            self.token_completion_total += response.usage.completion_tokens
            self.token_total += response.usage.total_tokens
        self.last_response_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "request_count": self.request_count,
            "response_count": self.response_count,
            "token_prompt_total": self.token_prompt_total,
            "token_completion_total": self.token_completion_total,
            "token_total": self.token_total,
            "duration_total": self.duration_total,
            "first_token_time": self.first_token_time,
            "last_response_time": self.last_response_time,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Session Config
# =============================================================================

@dataclass(slots=True)
class SessionConfig:
    """
    Configuration for an AISession.

    Attributes
    ----------
    provider : str | None
        Default provider for this session.
    model : str | None
        Default model for this session.
    timeout : float | None
        Default timeout for requests.
    retries : int | None
        Default retry count.
    temperature : float | None
        Default temperature.
    max_tokens : int | None
        Default maximum tokens.
    metadata : dict[str, Any]
        Additional configuration metadata.
    """

    provider: str | None = None
    model: str | None = None
    timeout: float | None = None
    retries: int | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {}
        if self.provider is not None:
            result["provider"] = self.provider
        if self.model is not None:
            result["model"] = self.model
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.retries is not None:
            result["retries"] = self.retries
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionConfig:
        """Create from a dictionary."""
        return cls(
            provider=data.get("provider"),
            model=data.get("model"),
            timeout=data.get("timeout"),
            retries=data.get("retries"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Session History
# =============================================================================

class SessionHistory:
    """
    Tracks the history of a session (requests, responses, prompts, events).

    Attributes
    ----------
    requests : list[AIRequest]
        List of requests in order.
    responses : list[AIResponse]
        List of responses in order.
    prompts : list[Prompt]
        List of prompts in order.
    events : list[SessionEvent]
        List of events in order.
    max_entries : int
        Maximum number of entries to keep per list.
    """

    def __init__(self, max_entries: int = 1000):
        """
        Initialize the history.

        Parameters
        ----------
        max_entries : int, default=1000
            Maximum number of entries per list.
        """
        self._requests: list[AIRequest] = []
        self._responses: list[AIResponse] = []
        self._prompts: list[Prompt] = []
        self._events: list[SessionEvent] = []
        self._max_entries = max_entries

    @property
    def requests(self) -> list[AIRequest]:
        """Return a copy of the request list."""
        return self._requests.copy()

    @property
    def responses(self) -> list[AIResponse]:
        """Return a copy of the response list."""
        return self._responses.copy()

    @property
    def prompts(self) -> list[Prompt]:
        """Return a copy of the prompt list."""
        return self._prompts.copy()

    @property
    def events(self) -> list[SessionEvent]:
        """Return a copy of the event list."""
        return self._events.copy()

    def add_request(self, request: AIRequest) -> None:
        """Add a request to history."""
        self._append_and_trim(self._requests, request)

    def add_response(self, response: AIResponse) -> None:
        """Add a response to history."""
        self._append_and_trim(self._responses, response)

    def add_prompt(self, prompt: Prompt) -> None:
        """Add a prompt to history."""
        self._append_and_trim(self._prompts, prompt)

    def add_event(self, event: SessionEvent) -> None:
        """Add an event to history."""
        self._append_and_trim(self._events, event)

    def _append_and_trim(self, lst: list, item: Any) -> None:
        """Append item and trim if exceeding max_entries."""
        lst.append(item)
        if len(lst) > self._max_entries:
            lst[: len(lst) - self._max_entries] = []

    def clear(self) -> None:
        """Clear all history."""
        self._requests.clear()
        self._responses.clear()
        self._prompts.clear()
        self._events.clear()

    def latest_request(self) -> AIRequest | None:
        """Return the most recent request."""
        return self._requests[-1] if self._requests else None

    def latest_response(self) -> AIResponse | None:
        """Return the most recent response."""
        return self._responses[-1] if self._responses else None

    def latest_prompt(self) -> Prompt | None:
        """Return the most recent prompt."""
        return self._prompts[-1] if self._prompts else None

    def __len__(self) -> int:
        """Return the number of events (or max of lists)."""
        return len(self._events)

    def __iter__(self) -> Iterable[tuple[AIRequest | None, AIResponse | None, Prompt | None, SessionEvent | None]]:
        """
        Iterate over paired items (request, response, prompt, event) by index.
        This is a simplified iteration.
        """
        max_len = max(
            len(self._requests),
            len(self._responses),
            len(self._prompts),
            len(self._events),
        )
        for i in range(max_len):
            yield (
                self._requests[i] if i < len(self._requests) else None,
                self._responses[i] if i < len(self._responses) else None,
                self._prompts[i] if i < len(self._prompts) else None,
                self._events[i] if i < len(self._events) else None,
            )


# =============================================================================
# Session Validator
# =============================================================================

class SessionValidator:
    """
    Validates session state transitions and data.
    """

    @staticmethod
    def validate_transition(current: SessionState, new: SessionState) -> None:
        """
        Validate a state transition.

        Parameters
        ----------
        current : SessionState
            Current state.
        new : SessionState
            Proposed new state.

        Raises
        ------
        ValueError
            If the transition is invalid.
        """
        # allowed transitions
        transitions = {
            SessionState.CREATED: {SessionState.READY, SessionState.CLOSED},
            SessionState.READY: {SessionState.RUNNING, SessionState.CLOSED},
            SessionState.RUNNING: {SessionState.STREAMING, SessionState.COMPLETED, SessionState.FAILED, SessionState.CANCELLED, SessionState.CLOSED},
            SessionState.STREAMING: {SessionState.COMPLETED, SessionState.FAILED, SessionState.CANCELLED, SessionState.CLOSED},
            SessionState.COMPLETED: {SessionState.CLOSED},
            SessionState.FAILED: {SessionState.CLOSED, SessionState.READY},  # allow retry
            SessionState.CANCELLED: {SessionState.CLOSED},
            SessionState.CLOSED: set(),
        }
        allowed = transitions.get(current, set())
        if new not in allowed:
            raise ValueError(
                f"Invalid state transition from {current.value} to {new.value}."
            )


# =============================================================================
# AISession
# =============================================================================

class AISession:
    """
    An AI session managing a complete interaction lifecycle.

    Features:
        - Unique ID, timestamps
        - State management
        - Request/Response/Prompt history
        - Statistics and events
        - Metadata and tags
        - Streaming support
        - Serialization
        - Context manager

    Examples
    --------
    >>> session = AISession(provider="openrouter", model="gpt-4")
    >>> session.add_request(request)
    >>> session.add_response(response)
    >>> session.complete()
    >>> session.export_json()
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        config: SessionConfig | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ):
        """
        Initialize a new AISession.

        Parameters
        ----------
        provider : str | None, optional
            Default provider.
        model : str | None, optional
            Default model.
        config : SessionConfig | None, optional
            Configuration object.
        session_id : str | None, optional
            Custom session ID (auto-generated if not provided).
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.
        """
        self._id = session_id or self._generate_id()
        self._created_at = time.time()
        self._updated_at = self._created_at

        self._state = SessionState.CREATED
        self._config = config or SessionConfig()
        if provider is not None:
            self._config.provider = provider
        if model is not None:
            self._config.model = model

        self._metadata: dict[str, Any] = metadata or {}
        self._tags: set[str] = set(tags or [])
        self._attributes: dict[str, Any] = {}

        self._history = SessionHistory()
        self._statistics = SessionStatistics()

        # Streaming specific
        self._accumulated_text: str = ""
        self._first_token_time: float | None = None
        self._finish_reason: str | None = None
        self._current_response: AIResponse | None = None
        self._current_request: AIRequest | None = None

        # Event log (also stored in history, but we keep a quick reference)
        self._event_count: int = 0

        # Mark as ready after init
        self._transition_to(SessionState.READY)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Get the session ID."""
        return self._id

    @property
    def created_at(self) -> float:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> float:
        """Get the last update timestamp."""
        return self._updated_at

    @property
    def state(self) -> SessionState:
        """Get the current state."""
        return self._state

    @property
    def provider(self) -> str | None:
        """Get the default provider."""
        return self._config.provider

    @property
    def model(self) -> str | None:
        """Get the default model."""
        return self._config.model

    @property
    def config(self) -> SessionConfig:
        """Get the session configuration."""
        return self._config

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the session metadata."""
        return self._metadata

    @property
    def tags(self) -> set[str]:
        """Get the session tags."""
        return self._tags.copy()

    @property
    def history(self) -> SessionHistory:
        """Get the session history."""
        return self._history

    @property
    def statistics(self) -> SessionStatistics:
        """Get the session statistics."""
        return self._statistics

    @property
    def accumulated_text(self) -> str:
        """Get accumulated text from streaming."""
        return self._accumulated_text

    @property
    def first_token_time(self) -> float | None:
        """Get the time to first token in streaming."""
        return self._first_token_time

    @property
    def finish_reason(self) -> str | None:
        """Get the finish reason of the last response."""
        return self._finish_reason

    # ------------------------------------------------------------------
    # ID Generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique session ID."""
        import hashlib
        import uuid
        raw = f"{uuid.uuid4()}{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------

    def _transition_to(self, new_state: SessionState) -> None:
        """
        Transition to a new state.

        Parameters
        ----------
        new_state : SessionState
            The target state.

        Raises
        ------
        ValueError
            If the transition is invalid.
        """
        SessionValidator.validate_transition(self._state, new_state)
        self._state = new_state
        self._touch()
        self._record_event("state_change", {"from": self._state.value, "to": new_state.value})

    def ready(self) -> Self:
        """Mark the session as ready."""
        if self._state == SessionState.CREATED:
            self._transition_to(SessionState.READY)
        return self

    def running(self) -> Self:
        """Mark the session as running."""
        self._transition_to(SessionState.RUNNING)
        return self

    def streaming(self) -> Self:
        """Mark the session as streaming."""
        self._transition_to(SessionState.STREAMING)
        return self

    def complete(self) -> Self:
        """Mark the session as completed."""
        self._transition_to(SessionState.COMPLETED)
        return self

    def fail(self, error: str = "") -> Self:
        """
        Mark the session as failed.

        Parameters
        ----------
        error : str, default=""
            Error message.
        """
        self._transition_to(SessionState.FAILED)
        if error:
            self._record_event("error", {"message": error})
        return self

    def cancel(self) -> Self:
        """Cancel the session."""
        self._transition_to(SessionState.CANCELLED)
        return self

    def close(self) -> Self:
        """Close the session."""
        self._transition_to(SessionState.CLOSED)
        return self

    # ------------------------------------------------------------------
    # Touch / Update
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        """Update the last updated timestamp."""
        self._updated_at = time.time()

    # ------------------------------------------------------------------
    # Event Recording
    # ------------------------------------------------------------------

    def _record_event(self, event_type: str, data: dict[str, Any] | None = None, source: str | None = None) -> None:
        """Record an event."""
        event = SessionEvent(type=event_type, data=data, source=source)
        self._history.add_event(event)
        self._event_count += 1

    # ------------------------------------------------------------------
    # Request/Response Management
    # ------------------------------------------------------------------

    def add_request(self, request: AIRequest) -> Self:
        """
        Add a request to the session.

        Parameters
        ----------
        request : AIRequest
            The request to add.
        """
        self._current_request = request
        self._history.add_request(request)
        self._statistics.request_count += 1
        self._record_event("request_added", {"request_id": getattr(request, "id", None)})
        self._touch()
        return self

    def add_response(self, response: AIResponse) -> Self:
        """
        Add a response to the session.

        Parameters
        ----------
        response : AIResponse
            The response to add.
        """
        self._current_response = response
        self._history.add_response(response)
        self._statistics.update_with_response(response)
        if response.success:
            self._record_event("response_received", {"id": response.id})
        else:
            self._record_event("response_error", {"message": response.message})
        self._touch()
        return self

    def add_prompt(self, prompt: Prompt) -> Self:
        """
        Add a prompt to the session.

        Parameters
        ----------
        prompt : Prompt
            The prompt to add.
        """
        self._history.add_prompt(prompt)
        self._record_event("prompt_added", {"prompt_id": prompt.id})
        self._touch()
        return self

    def current_request(self) -> AIRequest | None:
        """Return the most recent request."""
        return self._current_request

    def current_response(self) -> AIResponse | None:
        """Return the most recent response."""
        return self._current_response

    def latest_prompt(self) -> Prompt | None:
        """Return the most recent prompt."""
        return self._history.latest_prompt()

    # ------------------------------------------------------------------
    # Streaming Support
    # ------------------------------------------------------------------

    def append_chunk(self, chunk: ResponseChunk) -> Self:
        """
        Append a ResponseChunk for streaming.

        Parameters
        ----------
        chunk : ResponseChunk
            The chunk to append.
        """
        # First chunk - record first token time
        if self._first_token_time is None and chunk.choices:
            self._first_token_time = time.time()
            self._statistics.first_token_time = self._first_token_time

        # Accumulate text from first choice if content exists
        if chunk.choices:
            choice = chunk.choices[0]
            if choice.message.content:
                self._accumulated_text += choice.message.content

        # Track finish reason
        if chunk.finish_reason:
            self._finish_reason = chunk.finish_reason

        # Merge into current response if it exists
        if self._current_response is not None and chunk.choices:
            # Merge the chunk into the response's choices
            # We'll use merge_stream method on AIResponse
            if hasattr(self._current_response, "merge_stream"):
                self._current_response.merge_stream(chunk)

        # Also store the chunk as an event
        self._record_event("chunk_received", {"chunk": chunk.to_dict()})
        self._touch()
        return self

    def merge_response(self, response: AIResponse) -> Self:
        """
        Merge a final response into the session (for streaming completion).

        Parameters
        ----------
        response : AIResponse
            The final response.
        """
        if self._current_response is not None:
            # Merge the response into the current one
            # This is a simplistic approach; better to use a dedicated merge
            self._current_response = response
        else:
            self._current_response = response
        self._record_event("response_merged", {"id": response.id})
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------

    def set_attribute(self, key: str, value: Any) -> Self:
        """
        Set a custom attribute.

        Parameters
        ----------
        key : str
            Attribute key.
        value : Any
            Attribute value.
        """
        self._attributes[key] = value
        self._touch()
        return self

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get a custom attribute.

        Parameters
        ----------
        key : str
            Attribute key.
        default : Any, optional
            Default if key not found.
        """
        return self._attributes.get(key, default)

    def remove_attribute(self, key: str) -> Self:
        """
        Remove a custom attribute.

        Parameters
        ----------
        key : str
            Attribute key.
        """
        self._attributes.pop(key, None)
        self._touch()
        return self

    def clear_attributes(self) -> Self:
        """Clear all custom attributes."""
        self._attributes.clear()
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def append_metadata(self, data: dict[str, Any]) -> Self:
        """
        Append metadata to the session.

        Parameters
        ----------
        data : dict[str, Any]
            Metadata to append.
        """
        self._metadata.update(data)
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    def add_tag(self, tag: str) -> Self:
        """
        Add a tag.

        Parameters
        ----------
        tag : str
            Tag to add.
        """
        self._tags.add(tag)
        self._touch()
        return self

    def remove_tag(self, tag: str) -> Self:
        """
        Remove a tag.

        Parameters
        ----------
        tag : str
            Tag to remove.
        """
        self._tags.discard(tag)
        self._touch()
        return self

    def has_tag(self, tag: str) -> bool:
        """
        Check if a tag exists.

        Parameters
        ----------
        tag : str
            Tag to check.
        """
        return tag in self._tags

    def clear_tags(self) -> Self:
        """Remove all tags."""
        self._tags.clear()
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    def duration(self) -> float:
        """
        Get the total duration of the session (from creation to now or close).

        Returns
        -------
        float
            Duration in seconds.
        """
        return time.time() - self._created_at

    # ------------------------------------------------------------------
    # Reset / Clone
    # ------------------------------------------------------------------

    def reset(self) -> Self:
        """
        Reset the session to its initial state (CREATED) while keeping ID and config.
        This clears all history, statistics, and accumulated data.
        """
        self._state = SessionState.CREATED
        self._history.clear()
        self._statistics = SessionStatistics()
        self._accumulated_text = ""
        self._first_token_time = None
        self._finish_reason = None
        self._current_request = None
        self._current_response = None
        self._attributes.clear()
        self._metadata.clear()
        self._tags.clear()
        self._event_count = 0
        self._touch()
        return self

    def clone(self) -> AISession:
        """
        Create a deep copy of the session.

        Returns
        -------
        AISession
            A new session with the same configuration and state (but new ID).
        """
        new_session = AISession(
            provider=self._config.provider,
            model=self._config.model,
            config=deepcopy(self._config),
            metadata=deepcopy(self._metadata),
            tags=list(self._tags),
        )
        # Copy attributes
        new_session._attributes = deepcopy(self._attributes)
        # Copy history (deep copy of entries)
        # We'll use the history.add methods but we need to clone the items
        # For simplicity, we'll just copy the lists directly
        new_session._history._requests = [deepcopy(req) for req in self._history._requests]
        new_session._history._responses = [deepcopy(resp) for resp in self._history._responses]
        new_session._history._prompts = [deepcopy(prompt) for prompt in self._history._prompts]
        new_session._history._events = [deepcopy(event) for event in self._history._events]
        # Copy statistics (recompute? or just copy)
        new_session._statistics = deepcopy(self._statistics)
        # Copy streaming state
        new_session._accumulated_text = self._accumulated_text
        new_session._first_token_time = self._first_token_time
        new_session._finish_reason = self._finish_reason
        # State copy (keep same state)
        new_session._state = self._state
        new_session._touch()
        return new_session

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def export_dict(self) -> dict[str, Any]:
        """
        Export the session to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """
        return {
            "id": self._id,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "state": self._state.value,
            "config": self._config.to_dict(),
            "metadata": self._metadata,
            "tags": list(self._tags),
            "attributes": self._attributes,
            "statistics": self._statistics.to_dict(),
            "history": {
                "requests": [req.to_dict() for req in self._history.requests],
                "responses": [resp.to_dict() for resp in self._history.responses],
                "prompts": [prompt.to_dict() for prompt in self._history.prompts],
                "events": [event.to_dict() for event in self._history.events],
            },
            "accumulated_text": self._accumulated_text,
            "first_token_time": self._first_token_time,
            "finish_reason": self._finish_reason,
        }

    @classmethod
    def import_dict(cls, data: dict[str, Any]) -> AISession:
        """
        Import a session from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        AISession
            A new session instance.
        """
        # Create session with basic config
        config = SessionConfig.from_dict(data.get("config", {}))
        session = AISession(
            provider=config.provider,
            model=config.model,
            config=config,
            session_id=data.get("id"),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
        )
        # Set state and timestamps
        session._created_at = data.get("created_at", time.time())
        session._updated_at = data.get("updated_at", session._created_at)
        session._state = SessionState(data["state"])
        session._attributes = data.get("attributes", {})

        # Restore history
        hist = data.get("history", {})
        for req_data in hist.get("requests", []):
            req = AIRequest.from_dict(req_data)  # Assuming AIRequest has from_dict
            session._history._requests.append(req)
        for resp_data in hist.get("responses", []):
            resp = AIResponse.from_dict(resp_data)  # Assuming AIResponse has from_dict
            session._history._responses.append(resp)
        for prompt_data in hist.get("prompts", []):
            prompt = Prompt.from_dict(prompt_data)  # Assuming Prompt has from_dict
            session._history._prompts.append(prompt)
        for event_data in hist.get("events", []):
            event = SessionEvent.from_dict(event_data)
            session._history._events.append(event)

        # Statistics
        stats_data = data.get("statistics", {})
        session._statistics = SessionStatistics(
            request_count=stats_data.get("request_count", 0),
            response_count=stats_data.get("response_count", 0),
            token_prompt_total=stats_data.get("token_prompt_total", 0),
            token_completion_total=stats_data.get("token_completion_total", 0),
            token_total=stats_data.get("token_total", 0),
            duration_total=stats_data.get("duration_total", 0.0),
            first_token_time=stats_data.get("first_token_time"),
            last_response_time=stats_data.get("last_response_time"),
            created_at=datetime.fromisoformat(stats_data.get("created_at", datetime.utcnow().isoformat())),
        )

        session._accumulated_text = data.get("accumulated_text", "")
        session._first_token_time = data.get("first_token_time")
        session._finish_reason = data.get("finish_reason")
        session._touch()
        return session

    def export_json(self) -> str:
        """Export the session to JSON."""
        return json.dumps(self.export_dict(), indent=2, ensure_ascii=False, default=str)

    @classmethod
    def import_json(cls, data: str) -> AISession:
        """Import a session from JSON."""
        return cls.import_dict(json.loads(data))

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def __enter__(self) -> Self:
        """Enter the context manager."""
        if self._state == SessionState.CREATED:
            self.ready()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if exc_type is not None:
            self.fail(str(exc_val))
        else:
            self.complete()
        self.close()

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Check equality by ID."""
        if not isinstance(other, AISession):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash by ID."""
        return hash(self._id)

    def __len__(self) -> int:
        """Return the number of events."""
        return len(self._history)

    def __iter__(self):
        """Iterate over history events."""
        return iter(self._history)

    def __repr__(self) -> str:
        state = self._state.value.upper()
        provider = self._config.provider or "?"
        model = self._config.model or "?"
        return (
            f"<AISession id={self._id} state={state} "
            f"provider={provider} model={model} "
            f"requests={self._statistics.request_count} "
            f"responses={self._statistics.response_count}>"
        )

    def __str__(self) -> str:
        return self.__repr__()

    # ------------------------------------------------------------------
    # Additional Convenience Methods
    # ------------------------------------------------------------------

    def with_provider(self, provider: str) -> Self:
        """Set provider and return self."""
        self._config.provider = provider
        return self

    def with_model(self, model: str) -> Self:
        """Set model and return self."""
        self._config.model = model
        return self

    def with_config(self, config: SessionConfig) -> Self:
        """Set config and return self."""
        self._config = config
        return self


# =============================================================================
# Session Factory
# =============================================================================

class SessionFactory:
    """
    Factory for creating AISession instances with default configurations.
    """

    @staticmethod
    def create(
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> AISession:
        """
        Create a new session.

        Parameters
        ----------
        provider : str | None, optional
            Provider name.
        model : str | None, optional
            Model name.
        **kwargs
            Additional arguments passed to AISession.

        Returns
        -------
        AISession
            A new session instance.
        """
        return AISession(provider=provider, model=model, **kwargs)

    @staticmethod
    def from_request(request: AIRequest) -> AISession:
        """
        Create a session from an AIRequest.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        AISession
            A new session with the request added.
        """
        session = AISession(provider=request.provider or "default", model=request.model or "default")
        session.add_request(request)
        return session

    @staticmethod
    def from_prompt(prompt: Prompt, provider: str | None = None, model: str | None = None) -> AISession:
        """
        Create a session from a Prompt.

        Parameters
        ----------
        prompt : Prompt
            The prompt.
        provider : str | None, optional
            Provider name.
        model : str | None, optional
            Model name.

        Returns
        -------
        AISession
            A new session with the prompt added.
        """
        session = AISession(provider=provider, model=model)
        session.add_prompt(prompt)
        return session