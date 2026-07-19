"""
===============================================================================
Hermes AI Response Engine

Canonical response object used by every provider.

This is NOT a simple dataclass.

It is the complete response engine supporting:
    - Success/error status
    - Multiple choices
    - Tool calls
    - Function calls
    - Usage statistics
    - Streaming chunks
    - Validation
    - Serialization
    - Factory methods

Every provider returns an AIResponse.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import json
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from hermes.ai.prompt import PromptRole  # For role consistency

# =============================================================================
# Response Message
# =============================================================================


@dataclass(slots=True)
class ResponseMessage:
    """
    A message returned inside a response choice.

    Attributes
    ----------
    role : PromptRole | str
        The role of the message (usually assistant or tool).
    content : str
        The message content.
    name : str | None, optional
        Optional name (for tool calls or multi-agent).
    tool_call_id : str | None, optional
        ID of the tool call this message responds to.
    """

    role: PromptRole | str
    content: str
    name: str | None = None
    tool_call_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {
            "role": self.role.value if isinstance(self.role, PromptRole) else self.role,
            "content": self.content,
        }
        if self.name is not None:
            result["name"] = self.name
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResponseMessage:
        """Create from a dictionary."""
        role = data["role"]
        if isinstance(role, str):
            try:
                role = PromptRole(role)
            except ValueError:
                pass  # Keep as string
        return cls(
            role=role,
            content=data["content"],
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
        )


# =============================================================================
# Function Call
# =============================================================================


@dataclass(slots=True)
class FunctionCall:
    """
    A function call made by the model.

    Attributes
    ----------
    name : str
        The name of the function to call.
    arguments : dict[str, Any] | str
        The arguments to the function (parsed dict or JSON string).
    """

    name: str
    arguments: dict[str, Any] | str

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "name": self.name,
            "arguments": self.arguments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FunctionCall:
        """Create from a dictionary."""
        return cls(
            name=data["name"],
            arguments=data.get("arguments", {}),
        )


# =============================================================================
# Tool Call
# =============================================================================


@dataclass(slots=True)
class ToolCall:
    """
    A tool call made by the model.

    Attributes
    ----------
    id : str
        Unique ID of the tool call.
    type : str
        The type of the tool call (usually "function").
    function : FunctionCall
        The function call details.
    """

    id: str
    type: str = "function"
    function: FunctionCall | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }
        if self.function is not None:
            result["function"] = self.function.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolCall:
        """Create from a dictionary."""
        func = None
        if "function" in data:
            func = FunctionCall.from_dict(data["function"])
        return cls(
            id=data["id"],
            type=data.get("type", "function"),
            function=func,
        )


# =============================================================================
# Response Choice
# =============================================================================


@dataclass(slots=True)
class ResponseChoice:
    """
    A single choice from a response.

    Attributes
    ----------
    index : int
        The choice index.
    message : ResponseMessage
        The message returned.
    finish_reason : str | None, optional
        The reason the generation finished (stop, length, tool_calls, etc.).
    """

    index: int
    message: ResponseMessage
    finish_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result = {
            "index": self.index,
            "message": self.message.to_dict(),
        }
        if self.finish_reason is not None:
            result["finish_reason"] = self.finish_reason
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResponseChoice:
        """Create from a dictionary."""
        return cls(
            index=data["index"],
            message=ResponseMessage.from_dict(data["message"]),
            finish_reason=data.get("finish_reason"),
        )


# =============================================================================
# Response Usage
# =============================================================================


@dataclass(slots=True)
class ResponseUsage:
    """
    Token usage statistics.

    Attributes
    ----------
    prompt_tokens : int
        Number of tokens in the prompt.
    completion_tokens : int
        Number of tokens in the completion.
    total_tokens : int
        Total tokens (prompt + completion).
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to a dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> ResponseUsage:
        """Create from a dictionary."""
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


# =============================================================================
# Response Chunk (for streaming)
# =============================================================================


@dataclass(slots=True)
class ResponseChunk:
    """
    A single chunk from a streaming response.

    Attributes
    ----------
    id : str | None
        The response ID (may be None for partial chunks).
    created : float | None
        Timestamp of the chunk.
    model : str | None
        The model used.
    choices : list[ResponseChoice] | None
        Partial choices (usually one).
    usage : ResponseUsage | None
        Usage stats (usually only at the end).
    finish_reason : str | None
        Finish reason if the stream ended.
    """

    id: str | None = None
    created: float | None = None
    model: str | None = None
    choices: list[ResponseChoice] | None = None
    usage: ResponseUsage | None = None
    finish_reason: str | None = None

    def is_final(self) -> bool:
        """Check if this chunk indicates the end of the stream."""
        return self.finish_reason is not None or (
            self.usage is not None and self.usage.total_tokens > 0
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result = {}
        if self.id is not None:
            result["id"] = self.id
        if self.created is not None:
            result["created"] = self.created
        if self.model is not None:
            result["model"] = self.model
        if self.choices is not None:
            result["choices"] = [c.to_dict() for c in self.choices]
        if self.usage is not None:
            result["usage"] = self.usage.to_dict()
        if self.finish_reason is not None:
            result["finish_reason"] = self.finish_reason
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResponseChunk:
        """Create from a dictionary."""
        choices = None
        if "choices" in data:
            choices = [ResponseChoice.from_dict(c) for c in data["choices"]]
        usage = None
        if "usage" in data:
            usage = ResponseUsage.from_dict(data["usage"])
        return cls(
            id=data.get("id"),
            created=data.get("created"),
            model=data.get("model"),
            choices=choices,
            usage=usage,
            finish_reason=data.get("finish_reason"),
        )


# =============================================================================
# Response Statistics
# =============================================================================


@dataclass(slots=True)
class ResponseStatistics:
    """
    Statistics about a response.

    Attributes
    ----------
    total_time : float
        Total time taken from request to response.
    first_token_time : float | None
        Time to first token (for streaming).
    token_count : int
        Total tokens in the response.
    char_count : int
        Total characters in the response content.
    choice_count : int
        Number of choices.
    tool_call_count : int
        Number of tool calls.
    function_call_count : int
        Number of function calls.
    created_at : datetime
        When statistics were computed.
    """

    total_time: float = 0.0
    first_token_time: float | None = None
    token_count: int = 0
    char_count: int = 0
    choice_count: int = 0
    tool_call_count: int = 0
    function_call_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "total_time": self.total_time,
            "first_token_time": self.first_token_time,
            "token_count": self.token_count,
            "char_count": self.char_count,
            "choice_count": self.choice_count,
            "tool_call_count": self.tool_call_count,
            "function_call_count": self.function_call_count,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Response Validator
# =============================================================================


class ResponseValidator:
    """
    Validates response objects.

    Static methods to check response consistency.
    """

    @staticmethod
    def validate_response(response: AIResponse) -> None:
        """
        Validate an AIResponse.

        Parameters
        ----------
        response : AIResponse
            Response to validate.

        Raises
        ------
        ValueError
            If validation fails.
        """
        if response.success and not response.choices and not response.result:
            raise ValueError(
                "A successful response must have at least one choice or a result."
            )
        if not response.success and not response.message:
            raise ValueError("An error response must have a message.")

    @staticmethod
    def validate_choice(choice: ResponseChoice) -> None:
        """
        Validate a ResponseChoice.

        Parameters
        ----------
        choice : ResponseChoice
            Choice to validate.

        Raises
        ------
        ValueError
            If validation fails.
        """
        if not choice.message.content and not choice.message.tool_call_id:
            raise ValueError("A choice must have either content or a tool_call_id.")


# =============================================================================
# Response Serializer
# =============================================================================


class ResponseSerializer:
    """
    Serializes and deserializes AIResponse objects.

    Static methods only.
    """

    @staticmethod
    def to_dict(response: AIResponse) -> dict[str, Any]:
        """
        Serialize an AIResponse to a dictionary.

        Parameters
        ----------
        response : AIResponse
            Response to serialize.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """
        result: dict[str, Any] = {
            "success": response.success,
            "message": response.message,
            "result": response.result,
            "provider": response.provider,
            "model": response.model,
            "id": response.id,
            "created": response.created,
            "finish_reason": response.finish_reason,
            "duration": response.duration,
            "choices": [c.to_dict() for c in response.choices],
            "tool_calls": [t.to_dict() for t in response.tool_calls],
            "function_calls": [f.to_dict() for f in response.function_calls],
            "usage": response.usage.to_dict() if response.usage else None,
            "metadata": response.metadata,
            "raw": response.raw,
        }
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AIResponse:
        """
        Deserialize an AIResponse from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        choices = [ResponseChoice.from_dict(c) for c in data.get("choices", [])]
        tool_calls = [ToolCall.from_dict(t) for t in data.get("tool_calls", [])]
        function_calls = [
            FunctionCall.from_dict(f) for f in data.get("function_calls", [])
        ]
        usage = None
        if "usage" in data and data["usage"]:
            usage = ResponseUsage.from_dict(data["usage"])

        return AIResponse(
            success=data["success"],
            message=data.get("message", ""),
            result=data.get("result"),
            provider=data.get("provider", ""),
            model=data.get("model", ""),
            id=data.get("id", ""),
            created=data.get("created", 0.0),
            finish_reason=data.get("finish_reason"),
            duration=data.get("duration", 0.0),
            choices=choices,
            tool_calls=tool_calls,
            function_calls=function_calls,
            usage=usage,
            metadata=data.get("metadata", {}),
            raw=data.get("raw"),
        )

    @staticmethod
    def to_json(response: AIResponse) -> str:
        """
        Serialize an AIResponse to JSON.

        Parameters
        ----------
        response : AIResponse
            Response to serialize.

        Returns
        -------
        str
            JSON string.
        """
        return json.dumps(
            ResponseSerializer.to_dict(response),
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def from_json(data: str) -> AIResponse:
        """
        Deserialize an AIResponse from JSON.

        Parameters
        ----------
        data : str
            JSON string.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        return ResponseSerializer.from_dict(json.loads(data))


# =============================================================================
# Response Factory
# =============================================================================


class ResponseFactory:
    """
    Factory for creating AIResponse objects.

    Provides convenience methods for common response patterns.
    """

    @staticmethod
    def text(
        content: str,
        provider: str = "",
        model: str = "",
        id: str = "",
        finish_reason: str = "stop",
        usage: ResponseUsage | None = None,
        **kwargs,
    ) -> AIResponse:
        """
        Create a simple text response.

        Parameters
        ----------
        content : str
            The response text.
        provider : str, default=""
            Provider name.
        model : str, default=""
            Model name.
        id : str, default=""
            Response ID.
        finish_reason : str, default="stop"
            Finish reason.
        usage : ResponseUsage | None, optional
            Usage statistics.
        **kwargs
            Additional metadata.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        choice = ResponseChoice(
            index=0,
            message=ResponseMessage(role=PromptRole.ASSISTANT, content=content),
            finish_reason=finish_reason,
        )
        return AIResponse(
            success=True,
            result=content,
            provider=provider,
            model=model,
            id=id,
            finish_reason=finish_reason,
            choices=[choice],
            usage=usage,
            metadata=kwargs,
        )

    @staticmethod
    def error(
        message: str,
        provider: str = "",
        model: str = "",
        **kwargs,
    ) -> AIResponse:
        """
        Create an error response.

        Parameters
        ----------
        message : str
            Error message.
        provider : str, default=""
            Provider name.
        model : str, default=""
            Model name.
        **kwargs
            Additional metadata.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        return AIResponse(
            success=False,
            message=message,
            provider=provider,
            model=model,
            metadata=kwargs,
        )

    @staticmethod
    def tool(
        tool_calls: list[ToolCall],
        provider: str = "",
        model: str = "",
        id: str = "",
        **kwargs,
    ) -> AIResponse:
        """
        Create a response with tool calls.

        Parameters
        ----------
        tool_calls : list[ToolCall]
            List of tool calls.
        provider : str, default=""
            Provider name.
        model : str, default=""
            Model name.
        id : str, default=""
            Response ID.
        **kwargs
            Additional metadata.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        return AIResponse(
            success=True,
            provider=provider,
            model=model,
            id=id,
            tool_calls=tool_calls,
            metadata=kwargs,
        )

    @staticmethod
    def stream(
        provider: str = "",
        model: str = "",
        **kwargs,
    ) -> AIResponse:
        """
        Create an empty response for streaming.

        Parameters
        ----------
        provider : str, default=""
            Provider name.
        model : str, default=""
            Model name.
        **kwargs
            Additional metadata.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        return AIResponse(
            success=True,
            provider=provider,
            model=model,
            metadata=kwargs,
        )

    @staticmethod
    def empty() -> AIResponse:
        """
        Create an empty response.

        Returns
        -------
        AIResponse
            A new AIResponse instance.
        """
        return AIResponse(success=False, message="Empty response")


# =============================================================================
# AIResponse (Main Class)
# =============================================================================


class AIResponse:
    """
    The canonical response object in Hermes.

    This is returned by every provider.

    Features:
        - Success/error status
        - Multiple choices
        - Tool calls
        - Function calls
        - Usage statistics
        - Rich helpers (text(), is_success(), has_tool_calls(), etc.)
        - Serialization
        - Cloning
        - Streaming merge

    Examples
    --------
    >>> response = AIResponse.text("Hello, world!")
    >>> print(response.text())
    "Hello, world!"
    >>> response.is_success()
    True
    """

    def __init__(
        self,
        success: bool = False,
        message: str = "",
        result: Any = None,
        provider: str = "",
        model: str = "",
        id: str = "",
        created: float | None = None,
        finish_reason: str | None = None,
        duration: float = 0.0,
        choices: list[ResponseChoice] | None = None,
        tool_calls: list[ToolCall] | None = None,
        function_calls: list[FunctionCall] | None = None,
        usage: ResponseUsage | None = None,
        metadata: dict[str, Any] | None = None,
        raw: Any = None,
    ):
        """
        Initialize an AIResponse.

        Parameters
        ----------
        success : bool, default=False
            Whether the response was successful.
        message : str, default=""
            A message (usually error text).
        result : Any, optional
            A simple result (for simple generation).
        provider : str, default=""
            Provider name.
        model : str, default=""
            Model name.
        id : str, default=""
            Response ID from provider.
        created : float | None, optional
            Creation timestamp.
        finish_reason : str | None, optional
            Finish reason.
        duration : float, default=0.0
            Duration of the request.
        choices : list[ResponseChoice] | None, optional
            List of choices.
        tool_calls : list[ToolCall] | None, optional
            List of tool calls.
        function_calls : list[FunctionCall] | None, optional
            List of function calls.
        usage : ResponseUsage | None, optional
            Token usage.
        metadata : dict[str, Any] | None, optional
            Additional metadata.
        raw : Any, optional
            Raw provider response (for debugging).
        """
        self.success = success
        self.message = message
        self.result = result
        self.provider = provider
        self.model = model
        self.id = id
        self.created = created or time.time()
        self.finish_reason = finish_reason
        self.duration = duration
        self.choices = choices or []
        self.tool_calls = tool_calls or []
        self.function_calls = function_calls or []
        self.usage = usage
        self.metadata = metadata or {}
        self.raw = raw

        # Internal cache
        self._statistics: ResponseStatistics | None = None

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def is_success(self) -> bool:
        """Return True if the response was successful."""
        return self.success

    def is_error(self) -> bool:
        """Return True if the response was an error."""
        return not self.success

    def has_tool_calls(self) -> bool:
        """Return True if the response contains tool calls."""
        return bool(self.tool_calls)

    def has_function_calls(self) -> bool:
        """Return True if the response contains function calls."""
        return bool(self.function_calls)

    def has_choices(self) -> bool:
        """Return True if the response contains choices."""
        return bool(self.choices)

    def text(self) -> str:
        """
        Get the primary text content from the response.

        Prefers:
            1. `result` if it's a string.
            2. The first choice's message content.
            3. Empty string.

        Returns
        -------
        str
            The response text.
        """
        if isinstance(self.result, str):
            return self.result
        if self.choices:
            return self.choices[0].message.content
        return ""

    def first_choice(self) -> ResponseChoice | None:
        """Return the first choice, if any."""
        return self.choices[0] if self.choices else None

    def first_tool_call(self) -> ToolCall | None:
        """Return the first tool call, if any."""
        return self.tool_calls[0] if self.tool_calls else None

    # ------------------------------------------------------------------
    # Clone & Copy
    # ------------------------------------------------------------------

    def clone(self) -> AIResponse:
        """
        Create a deep copy of the response.

        Returns
        -------
        AIResponse
            A new AIResponse instance with the same data.
        """
        return deepcopy(self)

    def copy(self) -> AIResponse:
        """Alias for clone."""
        return self.clone()

    # ------------------------------------------------------------------
    # Streaming Merge
    # ------------------------------------------------------------------

    def merge_stream(self, chunk: ResponseChunk) -> None:
        """
        Merge a ResponseChunk into this response (for streaming).

        This mutates the current response.

        Parameters
        ----------
        chunk : ResponseChunk
            The chunk to merge.
        """
        if chunk.id is not None:
            self.id = chunk.id
        if chunk.created is not None:
            self.created = chunk.created
        if chunk.model is not None:
            self.model = chunk.model
        if chunk.usage is not None:
            self.usage = chunk.usage
        if chunk.finish_reason is not None:
            self.finish_reason = chunk.finish_reason

        if chunk.choices:
            # Merge choices incrementally
            for c in chunk.choices:
                if c.index < len(self.choices):
                    # Update existing choice (merge message content)
                    existing = self.choices[c.index]
                    if c.message.content:
                        existing.message.content += c.message.content
                    if c.message.role:
                        existing.message.role = c.message.role
                    if c.message.tool_call_id:
                        existing.message.tool_call_id = c.message.tool_call_id
                    if c.finish_reason:
                        existing.finish_reason = c.finish_reason
                else:
                    # Append new choice
                    self.choices.append(c)

        # Invalidate cached statistics
        self._statistics = None

    # ------------------------------------------------------------------
    # Token Estimation
    # ------------------------------------------------------------------

    def estimate_tokens(self) -> int:
        """
        Estimate the token count of the response.

        Uses a simple heuristic: 4 characters ≈ 1 token.

        Returns
        -------
        int
            Estimated token count.
        """
        total_chars = 0
        if self.result and isinstance(self.result, str):
            total_chars += len(self.result)
        for choice in self.choices:
            total_chars += len(choice.message.content)
        if self.usage:
            return self.usage.total_tokens
        return (total_chars // 4) + 1

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> ResponseStatistics:
        """
        Compute statistics about the response.

        Returns
        -------
        ResponseStatistics
            Statistics object.
        """
        if self._statistics is not None:
            return self._statistics

        stats = ResponseStatistics()
        stats.total_time = self.duration

        # Count tokens
        stats.token_count = self.estimate_tokens()
        stats.choice_count = len(self.choices)

        # Count tool calls
        stats.tool_call_count = len(self.tool_calls)

        # Count function calls
        stats.function_call_count = len(self.function_calls)

        # Count characters
        if self.result and isinstance(self.result, str):
            stats.char_count += len(self.result)
        for choice in self.choices:
            stats.char_count += len(choice.message.content)

        self._statistics = stats
        return stats

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dictionary."""
        return ResponseSerializer.to_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AIResponse:
        """Deserialize from a dictionary."""
        return ResponseSerializer.from_dict(data)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return ResponseSerializer.to_json(self)

    @classmethod
    def from_json(cls, data: str) -> AIResponse:
        """Deserialize from JSON."""
        return ResponseSerializer.from_json(data)

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of choices."""
        return len(self.choices)

    def __bool__(self) -> bool:
        """Return True if the response is successful and has content."""
        return self.success and (bool(self.result) or bool(self.choices))

    def __str__(self) -> str:
        """Return the primary text."""
        return self.text()

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "ERROR"
        text_preview = self.text()[:50]
        return (
            f"AIResponse(status={status}, "
            f"provider={self.provider!r}, "
            f"model={self.model!r}, "
            f"text='{text_preview}...', "
            f"choices={len(self.choices)}, "
            f"tool_calls={len(self.tool_calls)})"
        )
