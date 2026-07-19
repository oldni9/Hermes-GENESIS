"""
===============================================================================
Hermes AI Conversation Engine

Canonical conversation engine for Hermes.

A conversation is higher-level than a Session.
It manages the entire interaction history, context, branches, and state.

Hierarchy:
    Conversation
     ├── Messages (with tree support)
     ├── Branches
     ├── Checkpoints (with undo/redo)
     ├── Statistics
     ├── Summary
     ├── Metadata
     └── Events

Features:
    - Message management (add, edit, delete, search)
    - Role-based message addition (user, assistant, system, tool, function)
    - Conversation branching and merging
    - Checkpointing and rollback (undo/redo)
    - Token estimation and context window management
    - Automatic trimming (with pin/archive support)
    - Summary generation (placeholder)
    - Metadata, tags, attributes
    - Pinned and archived messages
    - Streaming support (begin_stream, append_delta, finish_stream)
    - Message status (pending, streaming, completed, failed, cancelled)
    - Message tree (parent/child for retries)
    - Event system (on_message, on_delete, etc.)
    - Serialization (dict/JSON)
    - Validation
    - Rich magic methods

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import json
import time
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Iterable, Self

from hermes.ai.prompt import Prompt, PromptRole, PromptMessage
from hermes.ai.response import (
    AIResponse,
    ToolCall,
    FunctionCall,
)

# =============================================================================
# Enums
# =============================================================================


class ConversationState(str, Enum):
    """
    States of a Conversation.

    ACTIVE    - Normal conversation, accepting messages.
    PAUSED    - Temporarily paused (no new messages accepted).
    ARCHIVED  - Read-only, preserved for history.
    CLOSED    - Closed, no further operations.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    CLOSED = "closed"


class MessageStatus(str, Enum):
    """
    Status of a conversation message.

    PENDING   - Message is waiting to be processed.
    STREAMING - Message is being streamed.
    COMPLETED - Message is fully generated.
    FAILED    - Message generation failed.
    CANCELLED - Message was cancelled.
    """

    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Extend PromptRole to include FUNCTION
class PromptRole(str, Enum):
    """Standard roles for prompt messages, extended for conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"
    DEVELOPER = "developer"

    # Aliases
    AI = "assistant"
    HUMAN = "user"
    BOT = "assistant"


# =============================================================================
# Conversation Message
# =============================================================================


@dataclass(slots=True)
class ConversationMessage:
    """
    A single message in a conversation.

    Attributes
    ----------
    id : str
        Unique message ID.
    role : PromptRole | str
        The role of the sender.
    content : str
        The message content.
    status : MessageStatus
        Current status of the message.
    timestamp : float
        Creation timestamp.
    edited_at : float | None
        Last edit timestamp.
    parent_id : str | None
        ID of parent message (for threading/retries).
    children : list[str]
        IDs of child messages (for threading).
    metadata : dict[str, Any]
        Additional metadata.
    attachments : list[Any] | None
        Optional attachments.
    tool_calls : list[ToolCall] | None
        Tool calls associated with this message.
    function_calls : list[FunctionCall] | None
        Function calls associated with this message.
    pinned : bool
        Whether the message is pinned.
    archived : bool
        Whether the message is archived.
    deleted : bool
        Whether the message is logically deleted.
    """

    id: str
    role: PromptRole | str
    content: str
    status: MessageStatus = MessageStatus.COMPLETED
    timestamp: float = field(default_factory=time.time)
    edited_at: float | None = None
    parent_id: str | None = None
    children: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    attachments: list[Any] | None = None
    tool_calls: list[ToolCall] | None = None
    function_calls: list[FunctionCall] | None = None
    pinned: bool = False
    archived: bool = False
    deleted: bool = False

    # ------------------------------------------------------------------
    # Additional properties for PromptBuilder integration
    # ------------------------------------------------------------------

    @property
    def name(self) -> str | None:
        """Return the name from metadata, if present."""
        return self.metadata.get("name")

    @property
    def tool_call_id(self) -> str | None:
        """Return the tool_call_id from metadata, if present."""
        return self.metadata.get("tool_call_id")

    def to_prompt_message(self) -> PromptMessage:
        """
        Convert this conversation message to a PromptMessage for prompt assembly.

        Returns
        -------
        PromptMessage
            A PromptMessage representation.
        """
        return PromptMessage(
            role=self.role,
            content=self.content,
            name=self.name,
            tool_call_id=self.tool_call_id,
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "role": self.role.value if isinstance(self.role, PromptRole) else self.role,
            "content": self.content,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "parent_id": self.parent_id,
            "children": self.children,
            "metadata": self.metadata,
            "pinned": self.pinned,
            "archived": self.archived,
            "deleted": self.deleted,
        }
        if self.edited_at is not None:
            result["edited_at"] = self.edited_at
        if self.attachments is not None:
            result["attachments"] = self.attachments
        if self.tool_calls is not None:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.function_calls is not None:
            result["function_calls"] = [fc.to_dict() for fc in self.function_calls]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationMessage:
        """Create from a dictionary."""
        role = data["role"]
        if isinstance(role, str):
            try:
                role = PromptRole(role)
            except ValueError:
                pass
        status = data.get("status", "completed")
        if isinstance(status, str):
            try:
                status = MessageStatus(status)
            except ValueError:
                status = MessageStatus.COMPLETED

        tool_calls = None
        if "tool_calls" in data:
            tool_calls = [ToolCall.from_dict(tc) for tc in data["tool_calls"]]
        function_calls = None
        if "function_calls" in data:
            function_calls = [
                FunctionCall.from_dict(fc) for fc in data["function_calls"]
            ]

        return cls(
            id=data["id"],
            role=role,
            content=data["content"],
            status=status,
            timestamp=data.get("timestamp", time.time()),
            edited_at=data.get("edited_at"),
            parent_id=data.get("parent_id"),
            children=data.get("children", []),
            metadata=data.get("metadata", {}),
            attachments=data.get("attachments"),
            tool_calls=tool_calls,
            function_calls=function_calls,
            pinned=data.get("pinned", False),
            archived=data.get("archived", False),
            deleted=data.get("deleted", False),
        )


# =============================================================================
# Conversation History (View)
# =============================================================================


class ConversationHistory:
    """
    A view over a conversation's message list.

    Provides query, filtering, slicing, search, and iteration.

    This class does NOT own the messages; it holds a reference to the conversation's
    internal list and operates on it directly.
    """

    def __init__(self, messages: list[ConversationMessage]):
        """
        Initialize the history view.

        Parameters
        ----------
        messages : list[ConversationMessage]
            Reference to the conversation's message list.
        """
        self._messages = messages

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> Iterable[ConversationMessage]:
        return iter(self._messages)

    def __getitem__(self, index: int) -> ConversationMessage:
        return self._messages[index]

    def latest(self, count: int = 1) -> list[ConversationMessage]:
        """Get the latest N messages."""
        return self._messages[-count:]

    def first(self, count: int = 1) -> list[ConversationMessage]:
        """Get the first N messages."""
        return self._messages[:count]

    def search(
        self, text: str, case_sensitive: bool = False
    ) -> list[ConversationMessage]:
        """Search messages for a substring."""
        if not case_sensitive:
            text = text.lower()
            return [m for m in self._messages if text in m.content.lower()]
        return [m for m in self._messages if text in m.content]

    def filter(
        self,
        role: PromptRole | str | None = None,
        status: MessageStatus | str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
        deleted: bool | None = None,
    ) -> list[ConversationMessage]:
        """Filter messages by role, status, pinned, archived, deleted."""
        result = self._messages
        if role is not None:
            role_str = role.value if isinstance(role, PromptRole) else role
            result = [
                m
                for m in result
                if (m.role.value if isinstance(m.role, PromptRole) else m.role)
                == role_str
            ]
        if status is not None:
            status_str = status.value if isinstance(status, MessageStatus) else status
            result = [m for m in result if m.status.value == status_str]
        if pinned is not None:
            result = [m for m in result if m.pinned == pinned]
        if archived is not None:
            result = [m for m in result if m.archived == archived]
        if deleted is not None:
            result = [m for m in result if m.deleted == deleted]
        return result

    def slice(
        self, start: int | None = None, end: int | None = None
    ) -> list[ConversationMessage]:
        """Get a slice of messages."""
        return self._messages[start:end]

    def parents(self, message_id: str) -> list[ConversationMessage]:
        """Get all parent messages (ancestors) of a message."""
        result = []
        msg = next((m for m in self._messages if m.id == message_id), None)
        while msg and msg.parent_id:
            parent = next((m for m in self._messages if m.id == msg.parent_id), None)
            if parent:
                result.append(parent)
                msg = parent
            else:
                break
        return result

    def children(self, message_id: str) -> list[ConversationMessage]:
        """Get direct children of a message."""
        return [m for m in self._messages if m.parent_id == message_id]

    def descendants(self, message_id: str) -> list[ConversationMessage]:
        """Get all descendants of a message."""
        result = []
        stack = [message_id]
        while stack:
            mid = stack.pop()
            children = self.children(mid)
            for child in children:
                result.append(child)
                stack.append(child.id)
        return result


# =============================================================================
# Conversation Branch
# =============================================================================


@dataclass(slots=True)
class ConversationBranch:
    """
    A branch of a conversation.

    Branches allow forking the conversation to explore alternative paths.

    Attributes
    ----------
    id : str
        Unique branch ID.
    name : str
        Human-readable name for the branch.
    created_at : float
        Creation timestamp.
    messages : list[ConversationMessage]
        Messages in this branch.
    parent_branch_id : str | None
        ID of the parent branch, if any.
    metadata : dict[str, Any]
        Additional metadata.
    """

    id: str
    name: str
    created_at: float = field(default_factory=time.time)
    messages: list[ConversationMessage] = field(default_factory=list)
    parent_branch_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "messages": [msg.to_dict() for msg in self.messages],
            "parent_branch_id": self.parent_branch_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationBranch:
        """Create from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data.get("created_at", time.time()),
            messages=[
                ConversationMessage.from_dict(m) for m in data.get("messages", [])
            ],
            parent_branch_id=data.get("parent_branch_id"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Conversation Checkpoint
# =============================================================================


@dataclass(slots=True)
class ConversationCheckpoint:
    """
    A checkpoint capturing the state of a conversation.

    Attributes
    ----------
    id : str
        Unique checkpoint ID.
    name : str
        Human-readable name.
    created_at : float
        Creation timestamp.
    messages : list[ConversationMessage]
        Messages at the time of checkpoint.
    metadata : dict[str, Any]
        Additional metadata.
    """

    id: str
    name: str
    created_at: float = field(default_factory=time.time)
    messages: list[ConversationMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationCheckpoint:
        """Create from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data.get("created_at", time.time()),
            messages=[
                ConversationMessage.from_dict(m) for m in data.get("messages", [])
            ],
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Conversation Summary
# =============================================================================


@dataclass(slots=True)
class ConversationSummary:
    """
    A summary of a conversation.

    Attributes
    ----------
    content : str
        The summary text.
    created_at : float
        Creation timestamp.
    tokens : int | None
        Token count of the summary.
    metadata : dict[str, Any]
        Additional metadata.
    """

    content: str
    created_at: float = field(default_factory=time.time)
    tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "content": self.content,
            "created_at": self.created_at,
            "tokens": self.tokens,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationSummary:
        """Create from a dictionary."""
        return cls(
            content=data["content"],
            created_at=data.get("created_at", time.time()),
            tokens=data.get("tokens"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Conversation Statistics
# =============================================================================


@dataclass(slots=True)
class ConversationStatistics:
    """
    Statistics about a conversation.

    Attributes
    ----------
    message_count : int
        Total number of messages.
    user_count : int
        Number of user messages.
    assistant_count : int
        Number of assistant messages.
    system_count : int
        Number of system messages.
    tool_count : int
        Number of tool messages.
    function_count : int
        Number of function messages.
    pinned_count : int
        Number of pinned messages.
    archived_count : int
        Number of archived messages.
    prompt_tokens : int
        Total prompt tokens (estimated).
    completion_tokens : int
        Total completion tokens (estimated).
    total_tokens : int
        Total tokens.
    total_duration : float
        Total duration of all messages (sum of durations if tracked).
    first_message_time : float | None
        Timestamp of the first message.
    last_message_time : float | None
        Timestamp of the last message.
    created_at : datetime
        When statistics were computed.
    """

    message_count: int = 0
    user_count: int = 0
    assistant_count: int = 0
    system_count: int = 0
    tool_count: int = 0
    function_count: int = 0
    pinned_count: int = 0
    archived_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_duration: float = 0.0
    first_message_time: float | None = None
    last_message_time: float | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def update_with_response(self, response: AIResponse) -> None:
        """
        Update statistics with an AIResponse.

        This should be called when a response is added to the conversation.
        """
        if response.usage:
            self.completion_tokens += response.usage.completion_tokens
            self.prompt_tokens += response.usage.prompt_tokens
            self.total_tokens += response.usage.total_tokens
        if response.duration:
            self.total_duration += response.duration

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "message_count": self.message_count,
            "user_count": self.user_count,
            "assistant_count": self.assistant_count,
            "system_count": self.system_count,
            "tool_count": self.tool_count,
            "function_count": self.function_count,
            "pinned_count": self.pinned_count,
            "archived_count": self.archived_count,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "total_duration": self.total_duration,
            "first_message_time": self.first_message_time,
            "last_message_time": self.last_message_time,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Conversation Event
# =============================================================================


@dataclass(slots=True)
class ConversationEvent:
    """
    An event that occurs in the conversation lifecycle.

    Attributes
    ----------
    type : str
        Event type (e.g., "message_added", "message_edited", "message_deleted", etc.).
    timestamp : float
        Event timestamp.
    data : dict[str, Any] | None
        Event data.
    source : str | None
        Source of the event.
    """

    type: str
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {"type": self.type, "timestamp": self.timestamp}
        if self.data is not None:
            result["data"] = self.data
        if self.source is not None:
            result["source"] = self.source
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationEvent:
        """Create from dictionary."""
        return cls(
            type=data["type"],
            timestamp=data.get("timestamp", time.time()),
            data=data.get("data"),
            source=data.get("source"),
        )


# =============================================================================
# Conversation Validator
# =============================================================================


class ConversationValidator:
    """
    Validates conversation structure and messages.
    """

    @staticmethod
    def validate_message(message: ConversationMessage) -> None:
        """
        Validate a single message.

        Parameters
        ----------
        message : ConversationMessage
            The message to validate.

        Raises
        ------
        ValueError
            If validation fails.
        """
        if not message.id:
            raise ValueError("Message must have an ID.")
        if not message.role:
            raise ValueError("Message must have a role.")
        if (
            not message.content
            and not message.tool_calls
            and not message.function_calls
        ):
            raise ValueError(
                "Message must have content, tool_calls, or function_calls."
            )

    @staticmethod
    def validate_state_transition(
        current: ConversationState, new: ConversationState
    ) -> None:
        """
        Validate a state transition.

        Parameters
        ----------
        current : ConversationState
            Current state.
        new : ConversationState
            Proposed new state.

        Raises
        ------
        ValueError
            If transition is invalid.
        """
        allowed = {
            ConversationState.ACTIVE: {
                ConversationState.PAUSED,
                ConversationState.ARCHIVED,
                ConversationState.CLOSED,
            },
            ConversationState.PAUSED: {
                ConversationState.ACTIVE,
                ConversationState.ARCHIVED,
                ConversationState.CLOSED,
            },
            ConversationState.ARCHIVED: {
                ConversationState.ACTIVE,
                ConversationState.CLOSED,
            },
            ConversationState.CLOSED: set(),
        }
        if new not in allowed.get(current, set()):
            raise ValueError(f"Invalid transition from {current.value} to {new.value}.")


# =============================================================================
# Conversation Serializer
# =============================================================================


class ConversationSerializer:
    """
    Serializes and deserializes AIConversation objects.
    """

    @staticmethod
    def to_dict(conversation: AIConversation) -> dict[str, Any]:
        """Serialize to a dictionary."""
        return {
            "id": conversation.id,
            "title": conversation.title,
            "session_id": conversation.session_id,
            "state": conversation.state.value,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [msg.to_dict() for msg in conversation._messages],
            "branches": [branch.to_dict() for branch in conversation._branches],
            "checkpoints": [cp.to_dict() for cp in conversation._checkpoints],
            "summary": (
                conversation._summary.to_dict() if conversation._summary else None
            ),
            "metadata": conversation.metadata,
            "tags": list(conversation.tags),
            "attributes": conversation._attributes,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AIConversation:
        """Deserialize from a dictionary."""
        conv = AIConversation(
            title=data.get("title", ""),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            state=ConversationState(data["state"]),
        )
        conv._id = data["id"]
        conv._created_at = data.get("created_at", time.time())
        conv._updated_at = data.get("updated_at", conv._created_at)
        conv._messages = [
            ConversationMessage.from_dict(m) for m in data.get("messages", [])
        ]
        conv._branches = [
            ConversationBranch.from_dict(b) for b in data.get("branches", [])
        ]
        conv._checkpoints = [
            ConversationCheckpoint.from_dict(cp) for cp in data.get("checkpoints", [])
        ]
        if data.get("summary"):
            conv._summary = ConversationSummary.from_dict(data["summary"])
        conv._attributes = data.get("attributes", {})
        return conv

    @staticmethod
    def to_json(conversation: AIConversation) -> str:
        """Serialize to JSON."""
        return json.dumps(
            ConversationSerializer.to_dict(conversation),
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def from_json(data: str) -> AIConversation:
        """Deserialize from JSON."""
        return ConversationSerializer.from_dict(json.loads(data))


# =============================================================================
# Conversation Factory
# =============================================================================


class ConversationFactory:
    """
    Factory for creating AIConversation instances.
    """

    @staticmethod
    def create(
        title: str = "",
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> AIConversation:
        """
        Create a new conversation.

        Parameters
        ----------
        title : str, default=""
            Title of the conversation.
        session_id : str | None, optional
            ID of the parent session.
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.

        Returns
        -------
        AIConversation
            A new conversation.
        """
        return AIConversation(
            title=title, session_id=session_id, metadata=metadata, tags=tags
        )

    @staticmethod
    def from_prompt(
        prompt: Prompt, title: str = "", session_id: str | None = None
    ) -> AIConversation:
        """
        Create a conversation from a Prompt.

        Parameters
        ----------
        prompt : Prompt
            The prompt to initialize the conversation.
        title : str, default=""
            Title for the conversation.
        session_id : str | None, optional
            ID of the parent session.

        Returns
        -------
        AIConversation
            A new conversation with the prompt's messages converted.
        """
        conv = AIConversation(title=title, session_id=session_id)
        for msg in prompt.messages:
            conv.add_message(role=msg.role, content=msg.content, metadata=msg.metadata)
        return conv

    @staticmethod
    def from_session(session: AISession, title: str = "") -> AIConversation:
        """
        Create a conversation from an AISession.

        Parameters
        ----------
        session : AISession
            The session to convert.
        title : str, default=""
            Title for the conversation.

        Returns
        -------
        AIConversation
            A new conversation with the session's prompts and responses.
        """
        conv = AIConversation(
            title=title or f"Session {session.id}", session_id=session.id
        )
        # Add prompts and responses from session history
        for prompt in session.history.prompts:
            for msg in prompt.messages:
                conv.add_message(
                    role=msg.role, content=msg.content, metadata=msg.metadata
                )
        for response in session.history.responses:
            if response.choices:
                for choice in response.choices:
                    conv.add_message(
                        role=choice.message.role, content=choice.message.content
                    )
        return conv


# =============================================================================
# AIConversation
# =============================================================================


class AIConversation:
    """
    A conversation in Hermes.

    Manages the full interaction lifecycle, including messages, branches,
    checkpoints, summary, metadata, and state.

    Examples
    --------
    >>> conv = AIConversation(title="My Chat")
    >>> conv.add_user("Hello, how are you?")
    >>> conv.add_assistant("I'm fine, thank you!")
    >>> conv.statistics().message_count
    2
    """

    def __init__(
        self,
        title: str = "",
        session_id: str | None = None,
        state: ConversationState = ConversationState.ACTIVE,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ):
        """
        Initialize a new conversation.

        Parameters
        ----------
        title : str, default=""
            Title of the conversation.
        session_id : str | None, optional
            ID of the parent session.
        state : ConversationState, default=ConversationState.ACTIVE
            Initial state.
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.
        """
        self._id = self._generate_id()
        self.title = title
        self._session_id = session_id
        self._state = state
        self._created_at = time.time()
        self._updated_at = self._created_at

        self._messages: list[ConversationMessage] = []
        self._branches: list[ConversationBranch] = []
        self._checkpoints: list[ConversationCheckpoint] = []
        self._checkpoint_stack: deque = deque()  # For undo/redo
        self._undo_stack: deque = deque()  # stack of checkpoint IDs
        self._redo_stack: deque = deque()
        self._summary: ConversationSummary | None = None

        self.metadata: dict[str, Any] = metadata or {}
        self._tags: set[str] = set(tags or [])
        self._attributes: dict[str, Any] = {}

        self._history = ConversationHistory(self._messages)
        self._statistics = ConversationStatistics()
        self._event_listeners: dict[str, list[Callable]] = {}

        # Message index for fast lookup by ID
        self._message_index: dict[str, int] = {}  # id -> index

        # Streaming state
        self._streaming_message_id: str | None = None
        self._streaming_start_time: float | None = None
        self._streaming_accumulated: str = ""

        # Rebuild index
        self._rebuild_index()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Get the conversation ID."""
        return self._id

    @property
    def session_id(self) -> str | None:
        """Get the session ID."""
        return self._session_id

    @property
    def state(self) -> ConversationState:
        """Get the current state."""
        return self._state

    @property
    def created_at(self) -> float:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> float:
        """Get last update timestamp."""
        return self._updated_at

    @property
    def messages(self) -> list[ConversationMessage]:
        """Get a copy of messages."""
        return self._messages.copy()

    @property
    def tags(self) -> set[str]:
        """Get tags."""
        return self._tags.copy()

    @property
    def summary(self) -> ConversationSummary | None:
        """Get the conversation summary."""
        return self._summary

    @property
    def history(self) -> ConversationHistory:
        """Get the conversation history view."""
        return self._history

    @property
    def branches(self) -> list[ConversationBranch]:
        """Get a copy of branches."""
        return self._branches.copy()

    @property
    def streaming(self) -> bool:
        """Check if a stream is in progress."""
        return self._streaming_message_id is not None

    # ------------------------------------------------------------------
    # ID Generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID."""
        import hashlib
        import uuid

        raw = f"{uuid.uuid4()}{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # Index Management
    # ------------------------------------------------------------------

    def _rebuild_index(self) -> None:
        """Rebuild the message index."""
        self._message_index = {msg.id: idx for idx, msg in enumerate(self._messages)}

    def _update_index(self, message: ConversationMessage, index: int) -> None:
        """Update the index for a message."""
        self._message_index[message.id] = index

    def _remove_from_index(self, message_id: str) -> None:
        """Remove a message from the index."""
        self._message_index.pop(message_id, None)

    def _get_message_index(self, message_id: str) -> int:
        """Get index of a message by ID."""
        return self._message_index.get(message_id, -1)

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------

    def _transition_to(self, new_state: ConversationState) -> None:
        """Transition to a new state."""
        ConversationValidator.validate_state_transition(self._state, new_state)
        self._state = new_state
        self._touch()

    def pause(self) -> Self:
        """Pause the conversation."""
        self._transition_to(ConversationState.PAUSED)
        return self

    def activate(self) -> Self:
        """Activate the conversation."""
        self._transition_to(ConversationState.ACTIVE)
        return self

    def archive(self) -> Self:
        """Archive the conversation."""
        self._transition_to(ConversationState.ARCHIVED)
        return self

    def close(self) -> Self:
        """Close the conversation."""
        self._transition_to(ConversationState.CLOSED)
        return self

    def is_active(self) -> bool:
        """Check if the conversation is active."""
        return self._state == ConversationState.ACTIVE

    # ------------------------------------------------------------------
    # Touch / Update
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        """Update the last updated timestamp."""
        self._updated_at = time.time()

    def _emit_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Emit an event to all registered listeners."""
        event = ConversationEvent(type=event_type, data=data)
        for callback in self._event_listeners.get(event_type, []):
            callback(event)

    def on(self, event_type: str, callback: Callable) -> None:
        """Register an event listener."""
        self._event_listeners.setdefault(event_type, []).append(callback)

    def off(self, event_type: str, callback: Callable) -> None:
        """Unregister an event listener."""
        if event_type in self._event_listeners:
            self._event_listeners[event_type] = [
                cb for cb in self._event_listeners[event_type] if cb != callback
            ]

    # ------------------------------------------------------------------
    # Message Management
    # ------------------------------------------------------------------

    def add_message(
        self,
        role: PromptRole | str,
        content: str = "",
        status: MessageStatus | str = MessageStatus.COMPLETED,
        parent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        attachments: list[Any] | None = None,
        tool_calls: list[ToolCall] | None = None,
        function_calls: list[FunctionCall] | None = None,
        pinned: bool = False,
        archived: bool = False,
        name: str | None = None,
        tool_call_id: str | None = None,
    ) -> Self:
        """
        Add a message to the conversation.

        Parameters
        ----------
        role : PromptRole | str
            Role of the message.
        content : str, default=""
            Content of the message.
        status : MessageStatus | str, default=MessageStatus.COMPLETED
            Status of the message.
        parent_id : str | None, optional
            ID of the parent message (for threading).
        metadata : dict[str, Any] | None, optional
            Additional metadata.
        attachments : list[Any] | None, optional
            Attachments.
        tool_calls : list[ToolCall] | None, optional
            Tool calls.
        function_calls : list[FunctionCall] | None, optional
            Function calls.
        pinned : bool, default=False
            Whether to pin the message.
        archived : bool, default=False
            Whether to archive the message.
        name : str | None, optional
            Optional name for the message (useful for tool messages).
        tool_call_id : str | None, optional
            Tool call ID (for tool messages).

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        if self._state == ConversationState.CLOSED:
            raise ValueError("Conversation is closed, cannot add messages.")
        if self._state == ConversationState.ARCHIVED:
            raise ValueError("Conversation is archived, cannot add messages.")

        # Normalize role and status
        if isinstance(role, str):
            try:
                role = PromptRole(role)
            except ValueError:
                pass
        if isinstance(status, str):
            try:
                status = MessageStatus(status)
            except ValueError:
                status = MessageStatus.COMPLETED

        # For tool messages, we may need to set tool_call_id from parameter if not provided
        if role == PromptRole.TOOL and tool_call_id is None:
            raise ValueError("Tool messages require a tool_call_id.")

        msg = ConversationMessage(
            id=self._generate_id(),
            role=role,
            content=content,
            status=status,
            parent_id=parent_id,
            metadata=metadata or {},
            attachments=attachments,
            tool_calls=tool_calls,
            function_calls=function_calls,
            pinned=pinned,
            archived=archived,
        )

        # Add name to metadata if provided
        if name is not None:
            msg.metadata["name"] = name
        if tool_call_id is not None:
            msg.metadata["tool_call_id"] = tool_call_id

        ConversationValidator.validate_message(msg)
        self._messages.append(msg)
        self._update_index(msg, len(self._messages) - 1)

        # Update statistics
        self._statistics.message_count += 1
        role_str = role.value if isinstance(role, PromptRole) else role
        if role_str == "user":
            self._statistics.user_count += 1
        elif role_str == "assistant":
            self._statistics.assistant_count += 1
        elif role_str == "system":
            self._statistics.system_count += 1
        elif role_str == "tool":
            self._statistics.tool_count += 1
        elif role_str == "function":
            self._statistics.function_count += 1
        if pinned:
            self._statistics.pinned_count += 1
        if archived:
            self._statistics.archived_count += 1
        if not self._statistics.first_message_time:
            self._statistics.first_message_time = msg.timestamp
        self._statistics.last_message_time = msg.timestamp

        self._touch()
        self._emit_event("message_added", {"message_id": msg.id})
        return self

    def add_user(self, content: str, **kwargs) -> Self:
        """Add a user message."""
        return self.add_message(PromptRole.USER, content, **kwargs)

    def add_assistant(self, content: str, **kwargs) -> Self:
        """Add an assistant message."""
        return self.add_message(PromptRole.ASSISTANT, content, **kwargs)

    # The following aliases are kept for backward compatibility
    def user(self, content: str, **kwargs) -> Self:
        """Alias for add_user()."""
        return self.add_user(content, **kwargs)

    def assistant(self, content: str, **kwargs) -> Self:
        """Alias for add_assistant()."""
        return self.add_assistant(content, **kwargs)

    # ------------------------------------------------------------------
    # Remaining existing methods (unchanged)
    # ------------------------------------------------------------------

    def system(self, content: str, **kwargs) -> Self:
        """Add a system message."""
        return self.add_message(PromptRole.SYSTEM, content, **kwargs)

    def tool(
        self, content: str, tool_call_id: str, name: str | None = None, **kwargs
    ) -> Self:
        """Add a tool message."""
        return self.add_message(
            PromptRole.TOOL, content, tool_call_id=tool_call_id, name=name, **kwargs
        )

    def function(self, content: str, name: str | None = None, **kwargs) -> Self:
        """Add a function message."""
        return self.add_message(PromptRole.FUNCTION, content, name=name, **kwargs)

    def latest(self, count: int = 1) -> list[ConversationMessage]:
        """Get the latest N messages."""
        return self._history.latest(count)

    def previous(self, count: int = 1, offset: int = 1) -> list[ConversationMessage]:
        """
        Get messages before the latest.

        Parameters
        ----------
        count : int, default=1
            Number of messages to get.
        offset : int, default=1
            Offset from the end.

        Returns
        -------
        list[ConversationMessage]
            List of previous messages.
        """
        start = len(self._messages) - offset - count
        end = len(self._messages) - offset
        if start < 0:
            start = 0
        return self._messages[start:end]

    def first(self, count: int = 1) -> list[ConversationMessage]:
        """Get the first N messages."""
        return self._history.first(count)

    def clear(self) -> Self:
        """Clear all messages and reset state."""
        self._messages.clear()
        self._message_index.clear()
        self._history = ConversationHistory(self._messages)
        self._statistics = ConversationStatistics()
        self._branches.clear()
        self._checkpoints.clear()
        self._checkpoint_stack.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._summary = None
        self._streaming_message_id = None
        self._streaming_start_time = None
        self._streaming_accumulated = ""
        self._touch()
        self._emit_event("cleared", {})
        return self

    def reset(self) -> Self:
        """Alias for clear."""
        return self.clear()

    def edit_message(
        self,
        message_id: str,
        content: str | None = None,
        status: MessageStatus | str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        """
        Edit a message by ID.

        Parameters
        ----------
        message_id : str
            ID of the message to edit.
        content : str | None, optional
            New content.
        status : MessageStatus | str | None, optional
            New status.
        metadata : dict[str, Any] | None, optional
            New metadata (merged).

        Returns
        -------
        Self
            The conversation (fluent API).

        Raises
        ------
        ValueError
            If message not found.
        """
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message with ID {message_id} not found.")
        msg = self._messages[idx]
        if content is not None:
            msg.content = content
            msg.edited_at = time.time()
        if status is not None:
            if isinstance(status, str):
                try:
                    status = MessageStatus(status)
                except ValueError:
                    status = MessageStatus.COMPLETED
            msg.status = status
        if metadata is not None:
            msg.metadata.update(metadata)
        self._touch()
        self._emit_event("message_edited", {"message_id": message_id})
        return self

    def delete_message(self, message_id: str, hard: bool = False) -> Self:
        """
        Delete a message by ID.

        Parameters
        ----------
        message_id : str
            ID of the message to delete.
        hard : bool, default=False
            If True, remove permanently; if False, mark as deleted.

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message with ID {message_id} not found.")
        if hard:
            self._messages.pop(idx)
            self._remove_from_index(message_id)
            self._rebuild_index()
        else:
            self._messages[idx].deleted = True
        self._touch()
        self._emit_event("message_deleted", {"message_id": message_id, "hard": hard})
        return self

    def pin_message(self, message_id: str) -> Self:
        """Pin a message."""
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message {message_id} not found.")
        self._messages[idx].pinned = True
        self._statistics.pinned_count += 1
        self._touch()
        self._emit_event("message_pinned", {"message_id": message_id})
        return self

    def unpin_message(self, message_id: str) -> Self:
        """Unpin a message."""
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message {message_id} not found.")
        self._messages[idx].pinned = False
        self._statistics.pinned_count -= 1
        self._touch()
        self._emit_event("message_unpinned", {"message_id": message_id})
        return self

    def archive_message(self, message_id: str) -> Self:
        """Archive a message."""
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message {message_id} not found.")
        self._messages[idx].archived = True
        self._statistics.archived_count += 1
        self._touch()
        self._emit_event("message_archived", {"message_id": message_id})
        return self

    def unarchive_message(self, message_id: str) -> Self:
        """Unarchive a message."""
        idx = self._get_message_index(message_id)
        if idx == -1:
            raise ValueError(f"Message {message_id} not found.")
        self._messages[idx].archived = False
        self._statistics.archived_count -= 1
        self._touch()
        self._emit_event("message_unarchived", {"message_id": message_id})
        return self

    def search_messages(
        self, text: str, case_sensitive: bool = False
    ) -> list[ConversationMessage]:
        """Search messages for a substring."""
        return self._history.search(text, case_sensitive)

    def filter_messages(
        self,
        role: PromptRole | str | None = None,
        status: MessageStatus | str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
        deleted: bool | None = None,
    ) -> list[ConversationMessage]:
        """Filter messages by role, status, pinned, archived, deleted."""
        return self._history.filter(role, status, pinned, archived, deleted)

    def estimate_tokens(self) -> int:
        """
        Estimate total tokens in the conversation.

        Uses a heuristic (4 chars ≈ 1 token).
        """
        total_chars = 0
        for msg in self._messages:
            if msg.deleted:
                continue
            total_chars += len(msg.content)
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.function:
                        total_chars += len(tc.function.name)
                        total_chars += len(str(tc.function.arguments))
            if msg.function_calls:
                for fc in msg.function_calls:
                    total_chars += len(fc.name)
                    total_chars += len(str(fc.arguments))
        return (total_chars // 4) + 1

    def trim_to(self, max_tokens: int) -> Self:
        """
        Trim the conversation to fit within a token limit.

        Removes oldest non-pinned, non-archived messages until token estimate <= max_tokens.

        Parameters
        ----------
        max_tokens : int
            Maximum allowed tokens.

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        while self.estimate_tokens() > max_tokens and len(self._messages) > 1:
            # Remove oldest message that is not pinned, archived, or deleted
            removed = False
            for i, msg in enumerate(self._messages):
                if not msg.pinned and not msg.archived and not msg.deleted:
                    self._messages.pop(i)
                    self._remove_from_index(msg.id)
                    self._rebuild_index()
                    removed = True
                    break
            if not removed:
                break
            self._touch()
        self._emit_event("trimmed", {"max_tokens": max_tokens})
        return self

    def trim_percent(self, percent: float) -> Self:
        """
        Trim the conversation by removing a percentage of oldest non-pinned, non-archived messages.

        Parameters
        ----------
        percent : float
            Percentage of messages to remove (0-100).

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        if percent <= 0:
            return self
        if percent >= 100:
            self.clear()
            return self
        to_remove = int(len(self._messages) * (percent / 100))
        removed = 0
        for i, msg in enumerate(self._messages):
            if removed >= to_remove:
                break
            if not msg.pinned and not msg.archived and not msg.deleted:
                self._messages.pop(i)
                self._remove_from_index(msg.id)
                removed += 1
        self._rebuild_index()
        self._touch()
        self._emit_event("trimmed_percent", {"percent": percent})
        return self

    def visible_messages(self) -> list[ConversationMessage]:
        """Get non-deleted messages."""
        return [m for m in self._messages if not m.deleted]

    def messages(self, limit: int | None = None) -> list[ConversationMessage]:
        """
        Get messages, optionally limiting the count (oldest trimmed).

        Parameters
        ----------
        limit : int | None, optional
            Maximum number of messages to return. If None, returns all visible messages.

        Returns
        -------
        list[ConversationMessage]
            List of visible messages, with oldest trimmed if limit is specified.
        """
        visible = self.visible_messages()
        if limit is not None and len(visible) > limit:
            return visible[-limit:]
        return visible

    def prompt_messages(
        self, include_system: bool = True, include_tools: bool = True
    ) -> list[dict]:
        """
        Get messages in a format suitable for provider payloads.

        Parameters
        ----------
        include_system : bool, default=True
            Whether to include system messages.
        include_tools : bool, default=True
            Whether to include tool messages.

        Returns
        -------
        list[dict]
            List of messages as dicts with 'role' and 'content' (and optionally 'name' and 'tool_call_id').
        """
        result = []
        for msg in self._messages:
            if msg.deleted:
                continue
            if msg.role == PromptRole.SYSTEM and not include_system:
                continue
            if msg.role == PromptRole.TOOL and not include_tools:
                continue
            entry: dict = {
                "role": (
                    msg.role.value if isinstance(msg.role, PromptRole) else msg.role
                ),
                "content": msg.content,
            }
            name = msg.metadata.get("name")
            if name:
                entry["name"] = name
            tool_call_id = msg.metadata.get("tool_call_id")
            if tool_call_id:
                entry["tool_call_id"] = tool_call_id
            result.append(entry)
        return result

    def branch(self, name: str) -> ConversationBranch:
        """
        Create a new branch from the current conversation state.

        Parameters
        ----------
        name : str
            Name of the branch.

        Returns
        -------
        ConversationBranch
            The new branch.
        """
        branch = ConversationBranch(
            id=self._generate_id(),
            name=name,
            messages=self._messages.copy(),
            parent_branch_id=None,
        )
        self._branches.append(branch)
        self._emit_event("branch_created", {"branch_id": branch.id})
        return branch

    def merge_branch(self, branch_id: str) -> Self:
        """
        Merge a branch into the current conversation.

        Appends branch's messages to the current history, assigning new IDs to avoid duplicates.

        Parameters
        ----------
        branch_id : str
            ID of the branch to merge.

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        branch = next((b for b in self._branches if b.id == branch_id), None)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found.")
        # Deep copy messages and assign new IDs
        for msg in branch.messages:
            new_msg = deepcopy(msg)
            new_msg.id = self._generate_id()
            new_msg.parent_id = None  # Reset parent to avoid cross-branch references
            self._messages.append(new_msg)
            self._update_index(new_msg, len(self._messages) - 1)
        self._rebuild_index()
        self._touch()
        self._emit_event("branch_merged", {"branch_id": branch_id})
        return self

    def checkpoint(self, name: str) -> ConversationCheckpoint:
        """
        Create a checkpoint of the current conversation state.

        Parameters
        ----------
        name : str
            Name of the checkpoint.

        Returns
        -------
        ConversationCheckpoint
            The checkpoint.
        """
        cp = ConversationCheckpoint(
            id=self._generate_id(),
            name=name,
            messages=self._messages.copy(),
            metadata={},
        )
        self._checkpoints.append(cp)
        self._checkpoint_stack.append(cp.id)
        self._undo_stack.append(cp.id)
        self._redo_stack.clear()
        self._emit_event("checkpoint_created", {"checkpoint_id": cp.id})
        return cp

    def rollback(self, checkpoint_id: str) -> Self:
        """
        Rollback to a previous checkpoint.

        Parameters
        ----------
        checkpoint_id : str
            ID of the checkpoint.

        Returns
        -------
        Self
            The conversation (fluent API).

        Raises
        ------
        ValueError
            If checkpoint not found.
        """
        cp = next((c for c in self._checkpoints if c.id == checkpoint_id), None)
        if not cp:
            raise ValueError(f"Checkpoint {checkpoint_id} not found.")
        self._messages = cp.messages.copy()
        self._rebuild_index()
        self._touch()
        self._emit_event("checkpoint_restored", {"checkpoint_id": checkpoint_id})
        return self

    def undo(self) -> Self:
        """
        Undo the last action (revert to previous checkpoint).

        Returns
        -------
        Self
            The conversation (fluent API).

        Raises
        ------
        ValueError
            If no checkpoint to undo.
        """
        if not self._undo_stack:
            raise ValueError("Nothing to undo.")
        cp_id = self._undo_stack.pop()
        self._redo_stack.append(cp_id)
        return self.rollback(cp_id)

    def redo(self) -> Self:
        """
        Redo a previously undone action.

        Returns
        -------
        Self
            The conversation (fluent API).

        Raises
        ------
        ValueError
            If no checkpoint to redo.
        """
        if not self._redo_stack:
            raise ValueError("Nothing to redo.")
        cp_id = self._redo_stack.pop()
        self._undo_stack.append(cp_id)
        return self.rollback(cp_id)

    def begin_stream(
        self, assistant_message: str = "", parent_id: str | None = None
    ) -> str:
        """
        Begin a streaming response.

        Creates a new assistant message with status STREAMING.

        Parameters
        ----------
        assistant_message : str, default=""
            Initial content of the assistant message.
        parent_id : str | None, optional
            Parent message ID.

        Returns
        -------
        str
            ID of the streaming message.

        Raises
        ------
        RuntimeError
            If a stream is already in progress.
        """
        if self._streaming_message_id is not None:
            raise RuntimeError("A stream is already in progress.")

        # Add an assistant message with status STREAMING
        self.add_message(
            role=PromptRole.ASSISTANT,
            content=assistant_message,
            status=MessageStatus.STREAMING,
            parent_id=parent_id,
        )
        self._streaming_message_id = self._messages[-1].id
        self._streaming_start_time = time.time()
        self._streaming_accumulated = assistant_message
        self._emit_event("stream_started", {"message_id": self._streaming_message_id})
        return self._streaming_message_id

    def append_delta(self, delta: str) -> None:
        """
        Append a delta chunk to the streaming message.

        Parameters
        ----------
        delta : str
            Text chunk to append.

        Raises
        ------
        RuntimeError
            If no stream is in progress.
        """
        if self._streaming_message_id is None:
            raise RuntimeError("No stream in progress.")
        msg = self.get_message(self._streaming_message_id)
        if msg is None:
            raise ValueError(
                f"Streaming message {self._streaming_message_id} not found."
            )
        msg.content += delta
        self._streaming_accumulated += delta
        self._touch()
        self._emit_event(
            "stream_delta", {"message_id": self._streaming_message_id, "delta": delta}
        )

    def finish_stream(self, finish_reason: str = "stop") -> str:
        """
        Finish the streaming response.

        Marks the streaming message as COMPLETED.

        Parameters
        ----------
        finish_reason : str, default="stop"
            Reason for completion.

        Returns
        -------
        str
            ID of the completed message.

        Raises
        ------
        RuntimeError
            If no stream is in progress.
        """
        if self._streaming_message_id is None:
            raise RuntimeError("No stream in progress.")
        msg = self.get_message(self._streaming_message_id)
        if msg is None:
            raise ValueError(
                f"Streaming message {self._streaming_message_id} not found."
            )
        msg.status = MessageStatus.COMPLETED
        msg.metadata["finish_reason"] = finish_reason
        self._statistics.completion_tokens += self.estimate_tokens()  # rough estimate
        self._streaming_message_id = None
        self._streaming_start_time = None
        self._streaming_accumulated = ""
        self._touch()
        self._emit_event(
            "stream_finished", {"message_id": msg.id, "finish_reason": finish_reason}
        )
        return msg.id

    def cancel_stream(self) -> None:
        """
        Cancel the streaming response.

        Marks the streaming message as CANCELLED.
        """
        if self._streaming_message_id is None:
            return
        msg = self.get_message(self._streaming_message_id)
        if msg is not None:
            msg.status = MessageStatus.CANCELLED
        self._streaming_message_id = None
        self._streaming_start_time = None
        self._streaming_accumulated = ""
        self._emit_event("stream_cancelled", {})

    def get_message(self, message_id: str) -> ConversationMessage | None:
        """Get a message by ID."""
        idx = self._get_message_index(message_id)
        if idx == -1:
            return None
        return self._messages[idx]

    def set_summary(self, content: str, tokens: int | None = None) -> Self:
        """
        Set the conversation summary.

        Parameters
        ----------
        content : str
            Summary content.
        tokens : int | None, optional
            Token count of the summary.

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        self._summary = ConversationSummary(content=content, tokens=tokens)
        self._touch()
        self._emit_event("summary_updated", {"content": content})
        return self

    def generate_summary(self, token_limit: int = 200) -> Self:
        """
        Generate a summary (placeholder implementation).

        In production, this would call an LLM or summarization service.

        Parameters
        ----------
        token_limit : int, default=200
            Maximum tokens for the summary.

        Returns
        -------
        Self
            The conversation (fluent API).
        """
        if not self._messages:
            self._summary = ConversationSummary(content="No messages.")
            return self
        text = " ".join([m.content for m in self._messages[:5] if not m.deleted])
        if len(text) > 500:
            text = text[:500] + "..."
        self._summary = ConversationSummary(
            content=text, tokens=self.estimate_tokens() // 2
        )
        self._touch()
        self._emit_event("summary_generated", {"summary": text})
        return self

    def statistics(self) -> ConversationStatistics:
        """
        Compute statistics about the conversation.

        Returns
        -------
        ConversationStatistics
            Statistics object.
        """
        stats = ConversationStatistics()
        stats.message_count = len(self._messages)
        stats.first_message_time = (
            self._messages[0].timestamp if self._messages else None
        )
        stats.last_message_time = (
            self._messages[-1].timestamp if self._messages else None
        )

        for msg in self._messages:
            if msg.deleted:
                continue
            role = msg.role.value if isinstance(msg.role, PromptRole) else msg.role
            if role == "user":
                stats.user_count += 1
            elif role == "assistant":
                stats.assistant_count += 1
            elif role == "system":
                stats.system_count += 1
            elif role == "tool":
                stats.tool_count += 1
            elif role == "function":
                stats.function_count += 1
            if msg.pinned:
                stats.pinned_count += 1
            if msg.archived:
                stats.archived_count += 1

        stats.prompt_tokens = self._statistics.prompt_tokens
        stats.completion_tokens = self._statistics.completion_tokens
        stats.total_tokens = self._statistics.total_tokens
        stats.total_duration = self._statistics.total_duration

        return stats

    def append_metadata(self, data: dict[str, Any]) -> Self:
        """Append metadata."""
        self.metadata.update(data)
        self._touch()
        self._emit_event("metadata_updated", {"data": data})
        return self

    def set_attribute(self, key: str, value: Any) -> Self:
        """Set a custom attribute."""
        self._attributes[key] = value
        self._touch()
        self._emit_event("attribute_set", {"key": key, "value": value})
        return self

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get a custom attribute."""
        return self._attributes.get(key, default)

    def remove_attribute(self, key: str) -> Self:
        """Remove a custom attribute."""
        self._attributes.pop(key, None)
        self._touch()
        self._emit_event("attribute_removed", {"key": key})
        return self

    def clear_attributes(self) -> Self:
        """Clear all attributes."""
        self._attributes.clear()
        self._touch()
        self._emit_event("attributes_cleared", {})
        return self

    def add_tag(self, tag: str) -> Self:
        """Add a tag."""
        self._tags.add(tag)
        self._touch()
        self._emit_event("tag_added", {"tag": tag})
        return self

    def remove_tag(self, tag: str) -> Self:
        """Remove a tag."""
        self._tags.discard(tag)
        self._touch()
        self._emit_event("tag_removed", {"tag": tag})
        return self

    def has_tag(self, tag: str) -> bool:
        """Check if tag exists."""
        return tag in self._tags

    def clear_tags(self) -> Self:
        """Clear all tags."""
        self._tags.clear()
        self._touch()
        self._emit_event("tags_cleared", {})
        return self

    def clone(self) -> AIConversation:
        """
        Create a deep copy of the conversation with new IDs.

        Returns
        -------
        AIConversation
            A new conversation with the same state but new IDs.
        """
        new_conv = AIConversation(
            title=self.title,
            session_id=self._session_id,
            state=self._state,
            metadata=deepcopy(self.metadata),
            tags=list(self._tags),
        )
        # Copy messages with new IDs
        id_map = {}
        for msg in self._messages:
            new_msg = deepcopy(msg)
            new_msg.id = self._generate_id()
            id_map[msg.id] = new_msg.id
            # Update parent_id if it was referencing a message in the clone
            if msg.parent_id and msg.parent_id in id_map:
                new_msg.parent_id = id_map[msg.parent_id]
            # Update children list to use new IDs
            new_msg.children = [
                id_map.get(cid, cid) for cid in msg.children if cid in id_map
            ]
            new_conv._messages.append(new_msg)
        new_conv._rebuild_index()
        # Copy branches with new IDs
        for branch in self._branches:
            new_branch = deepcopy(branch)
            new_branch.id = self._generate_id()
            new_branch.messages = []
            for msg in branch.messages:
                new_msg = deepcopy(msg)
                new_msg.id = self._generate_id()
                # Update parent references if possible
                if msg.parent_id and msg.parent_id in id_map:
                    new_msg.parent_id = id_map[msg.parent_id]
                new_branch.messages.append(new_msg)
            new_conv._branches.append(new_branch)
        # Copy checkpoints
        for cp in self._checkpoints:
            new_cp = deepcopy(cp)
            new_cp.id = self._generate_id()
            new_cp.messages = []
            for msg in cp.messages:
                new_msg = deepcopy(msg)
                new_msg.id = self._generate_id()
                if msg.parent_id and msg.parent_id in id_map:
                    new_msg.parent_id = id_map[msg.parent_id]
                new_cp.messages.append(new_msg)
            new_conv._checkpoints.append(new_cp)
        # Copy summary
        if self._summary:
            new_conv._summary = deepcopy(self._summary)
        # Copy attributes
        new_conv._attributes = deepcopy(self._attributes)
        new_conv._touch()
        return new_conv

    def export_dict(self) -> dict[str, Any]:
        """Export to a dictionary."""
        return ConversationSerializer.to_dict(self)

    @classmethod
    def import_dict(cls, data: dict[str, Any]) -> AIConversation:
        """Import from a dictionary."""
        return ConversationSerializer.from_dict(data)

    def export_json(self) -> str:
        """Export to JSON."""
        return ConversationSerializer.to_json(self)

    @classmethod
    def import_json(cls, data: str) -> AIConversation:
        """Import from JSON."""
        return ConversationSerializer.from_json(data)

    def replay(self, callback: Callable) -> None:
        """
        Replay the conversation by calling a callback on each message.

        Parameters
        ----------
        callback : callable
            Function that takes a ConversationMessage and returns None.
        """
        for msg in self._messages:
            if not msg.deleted:
                callback(msg)

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> Iterable[ConversationMessage]:
        return iter(self._messages)

    def __getitem__(self, index: int) -> ConversationMessage:
        return self._messages[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AIConversation):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"<AIConversation id={self._id} title={self.title!r} messages={len(self._messages)} state={self._state.value}>"

    def __str__(self) -> str:
        return self.__repr__()

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        if exc_type is not None:
            self.close()
        else:
            self.archive()
        self.close()


# =============================================================================
# Verification Block
# =============================================================================

# ✓ Removed circular import of AISession, SessionState
# ✓ All existing functionality preserved
# ✓ Conversation maintains its own state independently
# ✓ No dependency on session.py (breaks circular dependency)
# ✓ Backward compatibility maintained
