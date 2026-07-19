"""
===============================================================================
Hermes AI Prompt Engine

Canonical representation of prompts inside Hermes.

This is NOT just a string template.
It is the central prompt engine supporting:

    - System prompts
    - User prompts
    - Assistant prompts
    - Tool prompts
    - Developer prompts
    - Conversation prompts
    - Template variables
    - Safe rendering
    - Strict mode
    - Validation
    - Serialization
    - Token estimation hooks

Every provider will eventually consume Prompt objects.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Self

from hermes.ai.request import AIRequest

# =============================================================================
# Prompt Role
# =============================================================================


class PromptRole(str, Enum):
    """
    Standard roles for prompt messages.

    Used across all providers internally.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    DEVELOPER = "developer"

    # Aliases for convenience
    AI = "assistant"
    HUMAN = "user"
    BOT = "assistant"


# =============================================================================
# Prompt Message
# =============================================================================


@dataclass(slots=True)
class PromptMessage:
    """
    A single message inside a Prompt.

    Attributes
    ----------
    role : PromptRole
        The role of the message sender.
    content : str
        The message content.
    name : str | None, optional
        Optional name for tool messages or multi-agent contexts.
    tool_call_id : str | None, optional
        ID of the tool call this message responds to.
    metadata : dict[str, Any], optional
        Additional metadata for the message.
    """

    role: PromptRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert message to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the message.
        """

        result: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }

        if self.name is not None:
            result["name"] = self.name
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptMessage:
        """
        Create a PromptMessage from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation of a message.

        Returns
        -------
        PromptMessage
            A new PromptMessage instance.
        """

        role = data["role"]
        if isinstance(role, str):
            role = PromptRole(role)

        return cls(
            role=role,
            content=data["content"],
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Prompt Variable
# =============================================================================


@dataclass(slots=True)
class PromptVariable:
    """
    A named variable used in prompt templates.

    Attributes
    ----------
    name : str
        Variable name.
    value : Any
        Variable value.
    required : bool, default=True
        Whether the variable must be provided.
    description : str, default=""
        Optional description.
    """

    name: str
    value: Any
    required: bool = True
    description: str = ""


# =============================================================================
# Prompt Template
# =============================================================================


@dataclass(slots=True)
class PromptTemplate:
    """
    A template with placeholders for variables.

    Attributes
    ----------
    template : str
        The template string with {variable} placeholders.
    variables : list[PromptVariable] | None, optional
        List of defined variables for this template.
    strict : bool, default=True
        If True, missing variables raise an error during rendering.
    """

    template: str
    variables: list[PromptVariable] | None = None
    strict: bool = True

    def render(self, context: dict[str, Any] | None = None) -> str:
        """
        Render the template with the given context.

        Parameters
        ----------
        context : dict[str, Any] | None, optional
            Variable values to use for rendering.

        Returns
        -------
        str
            The rendered template string.

        Raises
        ------
        ValueError
            If strict mode is enabled and a required variable is missing.
        """

        if context is None:
            context = {}

        # Build variable map from defined variables
        var_map: dict[str, Any] = {}
        if self.variables:
            for var in self.variables:
                var_map[var.name] = var.value

        # Override with provided context
        var_map.update(context)

        # Check for missing required variables
        if self.strict and self.variables:
            for var in self.variables:
                if var.required and var.name not in var_map:
                    raise ValueError(f"Missing required variable: '{var.name}'")

        try:
            return self.template.format(**var_map)
        except KeyError as e:
            if self.strict:
                raise ValueError(f"Missing variable: {e}") from e
            # Fallback: leave placeholder as-is
            return self.template

    def to_dict(self) -> dict[str, Any]:
        """
        Convert template to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """

        return {
            "template": self.template,
            "variables": [v.__dict__ for v in (self.variables or [])],
            "strict": self.strict,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptTemplate:
        """
        Create a PromptTemplate from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        PromptTemplate
            A new PromptTemplate instance.
        """

        variables = None
        if "variables" in data:
            variables = [PromptVariable(**v) for v in data["variables"]]

        return cls(
            template=data["template"],
            variables=variables,
            strict=data.get("strict", True),
        )


# =============================================================================
# Prompt Renderer
# =============================================================================


class PromptRenderer:
    """
    Renders prompt messages and templates.

    This is a utility class with static methods for rendering.
    """

    @staticmethod
    def render_messages(
        messages: list[PromptMessage],
    ) -> str:
        """
        Render messages as a single concatenated string.

        Parameters
        ----------
        messages : list[PromptMessage]
            Messages to render.

        Returns
        -------
        str
            Concatenated message content with role prefixes.
        """

        parts: list[str] = []

        for msg in messages:
            prefix = f"[{msg.role.value.upper()}]"
            if msg.name:
                prefix += f" ({msg.name})"
            parts.append(f"{prefix}\n{msg.content}")

        return "\n\n".join(parts)

    @staticmethod
    def render_conversation(
        messages: list[PromptMessage],
        include_roles: bool = True,
    ) -> str:
        """
        Render conversation in a human-readable format.

        Parameters
        ----------
        messages : list[PromptMessage]
            Messages to render.
        include_roles : bool, default=True
            Whether to include role labels.

        Returns
        -------
        str
            Conversation string.
        """

        if not include_roles:
            return "\n".join(msg.content for msg in messages)

        return PromptRenderer.render_messages(messages)


# =============================================================================
# Prompt Validator
# =============================================================================


class PromptValidator:
    """
    Validates prompt structure, messages, and variables.

    Static methods for validation.
    """

    @staticmethod
    def validate_messages(
        messages: list[PromptMessage],
        *,
        require_user: bool = True,
        require_system: bool = False,
        max_messages: int | None = None,
    ) -> None:
        """
        Validate a list of messages.

        Parameters
        ----------
        messages : list[PromptMessage]
            Messages to validate.
        require_user : bool, default=True
            Whether at least one user message is required.
        require_system : bool, default=False
            Whether a system message is required.
        max_messages : int | None, optional
            Maximum number of messages allowed.

        Raises
        ------
        ValueError
            If validation fails.
        """

        if not messages:
            raise ValueError("Messages list cannot be empty.")

        if max_messages is not None and len(messages) > max_messages:
            raise ValueError(
                f"Too many messages. Maximum: {max_messages}, got: {len(messages)}"
            )

        has_user = False
        has_system = False

        for msg in messages:
            if msg.role == PromptRole.USER:
                has_user = True
            if msg.role == PromptRole.SYSTEM:
                has_system = True

        if require_user and not has_user:
            raise ValueError("At least one user message is required.")

        if require_system and not has_system:
            raise ValueError("At least one system message is required.")

    @staticmethod
    def validate_variables(
        variables: list[PromptVariable],
        *,
        allow_unused: bool = True,
    ) -> None:
        """
        Validate variables.

        Parameters
        ----------
        variables : list[PromptVariable]
            Variables to validate.
        allow_unused : bool, default=True
            Whether unused variables are allowed.

        Raises
        ------
        ValueError
            If validation fails.
        """

        if not variables:
            return

        names = {v.name for v in variables}
        if len(names) != len(variables):
            raise ValueError("Duplicate variable names found.")

        for var in variables:
            if var.required and var.value is None:
                raise ValueError(f"Required variable '{var.name}' has no value.")


# =============================================================================
# Prompt Serializer
# =============================================================================


class PromptSerializer:
    """
    Serializes and deserializes Prompt objects to/from JSON/dict.

    Static methods only.
    """

    @staticmethod
    def to_dict(prompt: Prompt) -> dict[str, Any]:
        """
        Serialize a Prompt to a dictionary.

        Parameters
        ----------
        prompt : Prompt
            Prompt to serialize.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """

        return {
            "id": prompt.id,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat(),
            "system": prompt.system,
            "messages": [m.to_dict() for m in prompt.messages],
            "variables": [
                {
                    "name": v.name,
                    "value": v.value,
                    "required": v.required,
                    "description": v.description,
                }
                for v in prompt._variables.values()
            ],
            "template": prompt._template.template if prompt._template else None,
            "strict": prompt._strict,
            "metadata": prompt.metadata,
            "version": prompt.version,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Prompt:
        """
        Deserialize a dictionary to a Prompt.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        Prompt
            A new Prompt instance.
        """

        prompt = Prompt()

        if "id" in data:
            prompt._id = data["id"]
        if "created_at" in data:
            prompt._created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            prompt._updated_at = datetime.fromisoformat(data["updated_at"])

        if "system" in data:
            prompt.system = data["system"]

        if "messages" in data:
            prompt.messages = [PromptMessage.from_dict(m) for m in data["messages"]]

        if "variables" in data:
            for v in data["variables"]:
                prompt.set_variable(v["name"], v["value"], v.get("required", True))

        if "template" in data and data["template"]:
            prompt._template = PromptTemplate(
                template=data["template"],
                strict=data.get("strict", True),
            )

        if "strict" in data:
            prompt._strict = data["strict"]

        if "metadata" in data:
            prompt.metadata.update(data["metadata"])

        return prompt

    @staticmethod
    def to_json(prompt: Prompt) -> str:
        """
        Serialize a Prompt to JSON.

        Parameters
        ----------
        prompt : Prompt
            Prompt to serialize.

        Returns
        -------
        str
            JSON string.
        """

        return json.dumps(
            PromptSerializer.to_dict(prompt),
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def from_json(data: str) -> Prompt:
        """
        Deserialize a Prompt from JSON.

        Parameters
        ----------
        data : str
            JSON string.

        Returns
        -------
        Prompt
            A new Prompt instance.
        """

        return PromptSerializer.from_dict(json.loads(data))


# =============================================================================
# Prompt Parser
# =============================================================================


class PromptParser:
    """
    Parses raw text into structured Prompt objects.

    Future implementations may support:
        - Markdown frontmatter
        - YAML frontmatter
        - DSL for roles
    """

    @staticmethod
    def parse_text(
        text: str,
        role: PromptRole = PromptRole.USER,
    ) -> PromptMessage:
        """
        Parse raw text into a single message.

        Parameters
        ----------
        text : str
            Raw text content.
        role : PromptRole, default=PromptRole.USER
            Role to assign to the message.

        Returns
        -------
        PromptMessage
            A single message.
        """

        return PromptMessage(role=role, content=text)

    @staticmethod
    def parse_messages(
        text: str,
        delimiter: str = "\n---\n",
    ) -> list[PromptMessage]:
        """
        Parse text into multiple messages using a delimiter.

        Each segment is assigned the user role.

        Parameters
        ----------
        text : str
            Raw text content.
        delimiter : str, default="\\n---\\n"
            Separator between messages.

        Returns
        -------
        list[PromptMessage]
            List of messages.
        """

        if not text:
            return []

        segments = text.split(delimiter)

        return [
            PromptMessage(
                role=PromptRole.USER,
                content=seg.strip(),
            )
            for seg in segments
            if seg.strip()
        ]


# =============================================================================
# Prompt History
# =============================================================================


@dataclass(slots=True)
class PromptHistory:
    """
    Maintains a history of prompts and their states.

    Attributes
    ----------
    entries : list[Prompt]
        List of historical prompt snapshots.
    max_entries : int
        Maximum number of entries to keep.
    """

    entries: list[Prompt] = field(default_factory=list)
    max_entries: int = 100

    def add(self, prompt: Prompt) -> None:
        """
        Add a snapshot of a prompt to history.

        Parameters
        ----------
        prompt : Prompt
            Prompt to snapshot.
        """

        self.entries.append(prompt.clone())

        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def clear(self) -> None:
        """Clear all history entries."""

        self.entries.clear()

    def latest(self) -> Prompt | None:
        """
        Get the most recent prompt.

        Returns
        -------
        Prompt | None
            Most recent prompt, or None if empty.
        """

        return self.entries[-1] if self.entries else None

    def count(self) -> int:
        """
        Get the number of entries in history.

        Returns
        -------
        int
            Number of entries.
        """

        return len(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterable[Prompt]:
        return iter(self.entries)


# =============================================================================
# Prompt Statistics
# =============================================================================


@dataclass(slots=True)
class PromptStatistics:
    """
    Statistics about a Prompt.

    Attributes
    ----------
    message_count : int
        Total number of messages.
    system_count : int
        Number of system messages.
    user_count : int
        Number of user messages.
    assistant_count : int
        Number of assistant messages.
    tool_count : int
        Number of tool messages.
    variable_count : int
        Number of variables.
    total_chars : int
        Total character count (content only).
    estimated_tokens : int
        Estimated token count.
    has_template : bool
        Whether a template is present.
    created_at : datetime
        When statistics were computed.
    """

    message_count: int = 0
    system_count: int = 0
    user_count: int = 0
    assistant_count: int = 0
    tool_count: int = 0
    variable_count: int = 0
    total_chars: int = 0
    estimated_tokens: int = 0
    has_template: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to a dictionary."""

        return {
            "message_count": self.message_count,
            "system_count": self.system_count,
            "user_count": self.user_count,
            "assistant_count": self.assistant_count,
            "tool_count": self.tool_count,
            "variable_count": self.variable_count,
            "total_chars": self.total_chars,
            "estimated_tokens": self.estimated_tokens,
            "has_template": self.has_template,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Prompt Factory
# =============================================================================


class PromptFactory:
    """
    Factory for creating Prompt objects from various sources.

    Provides convenience methods for common prompt patterns.
    """

    @staticmethod
    def chat(
        system: str = "",
        user: str = "",
        assistant: str = "",
        history: list[dict[str, str]] | None = None,
    ) -> Prompt:
        """
        Create a chat prompt.

        Parameters
        ----------
        system : str, default=""
            System instruction.
        user : str, default=""
            User message.
        assistant : str, default=""
            Assistant message (for few-shot).
        history : list[dict[str, str]] | None, optional
            List of {"role": "user"/"assistant", "content": str} entries.

        Returns
        -------
        Prompt
            A new Prompt.
        """

        prompt = Prompt()

        if system:
            prompt.add_system(system)

        if history:
            for entry in history:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role == "user":
                    prompt.add_user(content)
                elif role == "assistant":
                    prompt.add_assistant(content)

        if user:
            prompt.add_user(user)

        if assistant:
            prompt.add_assistant(assistant)

        return prompt

    @staticmethod
    def generate(prompt_text: str) -> Prompt:
        """
        Create a simple generation prompt.

        Parameters
        ----------
        prompt_text : str
            The prompt text.

        Returns
        -------
        Prompt
            A new Prompt with a single user message.
        """

        prompt = Prompt()
        prompt.add_user(prompt_text)
        return prompt

    @staticmethod
    def from_messages(messages: list[PromptMessage]) -> Prompt:
        """
        Create a Prompt from an existing list of messages.

        Parameters
        ----------
        messages : list[PromptMessage]
            List of messages.

        Returns
        -------
        Prompt
            A new Prompt with the messages.
        """

        prompt = Prompt()
        prompt.messages = messages.copy()
        return prompt


# =============================================================================
# Prompt (Main Class)
# =============================================================================


class Prompt:
    """
    The canonical prompt representation in Hermes.

    This is NOT just a string. It is a fully featured prompt engine.

    Features:
        - Multi-role messages (system, user, assistant, tool, developer)
        - Template variables with strict/lenient rendering
        - Validation (message structure, variables)
        - Serialization (JSON/dict)
        - Deep copy / clone
        - Merge / append / prepend
        - Token estimation (pluggable)
        - Statistics
        - History

    Integration:
        - to_request() creates an AIRequest ready for providers.

    Examples
    --------
    >>> prompt = Prompt()
    >>> prompt.add_system("You are a helpful assistant.")
    >>> prompt.add_user("What is Python?")
    >>> request = prompt.to_request()
    >>> print(request.prompt)  # "What is Python?"
    """

    def __init__(
        self,
        system: str = "",
        messages: list[PromptMessage] | None = None,
        template: str | None = None,
        strict: bool = True,
    ):
        """
        Initialize a Prompt.

        Parameters
        ----------
        system : str, default=""
            System instruction.
        messages : list[PromptMessage] | None, optional
            Initial messages.
        template : str | None, optional
            Template string with {variable} placeholders.
        strict : bool, default=True
            Strict mode for variable validation.
        """

        self._id: str = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        self._created_at: datetime = datetime.utcnow()
        self._updated_at: datetime = self._created_at

        self.system: str = system
        self.messages: list[PromptMessage] = messages or []
        self._variables: dict[str, PromptVariable] = {}
        self._template: PromptTemplate | None = None
        self._strict: bool = strict
        self.metadata: dict[str, Any] = {}
        self.version: str = "1.0"

        self._history: PromptHistory = PromptHistory()
        self._statistics: PromptStatistics | None = None

        if template is not None:
            self._template = PromptTemplate(template=template, strict=strict)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Get the prompt ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the last updated timestamp."""
        return self._updated_at

    @property
    def variables(self) -> list[PromptVariable]:
        """Get all variables as a list."""
        return list(self._variables.values())

    # ------------------------------------------------------------------
    # Message Management
    # ------------------------------------------------------------------

    def add_message(
        self,
        role: PromptRole | str,
        content: str,
        name: str | None = None,
        tool_call_id: str | None = None,
    ) -> Self:
        """
        Add a message to the prompt.

        Parameters
        ----------
        role : PromptRole | str
            Role of the message.
        content : str
            Message content.
        name : str | None, optional
            Optional name.
        tool_call_id : str | None, optional
            Tool call ID for tool responses.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        if isinstance(role, str):
            role = PromptRole(role)

        self.messages.append(
            PromptMessage(
                role=role,
                content=content,
                name=name,
                tool_call_id=tool_call_id,
            )
        )

        self._touch()
        return self

    def add_system(self, content: str) -> Self:
        """Add a system message."""
        return self.add_message(PromptRole.SYSTEM, content)

    def add_user(self, content: str, name: str | None = None) -> Self:
        """Add a user message."""
        return self.add_message(PromptRole.USER, content, name=name)

    def add_assistant(
        self,
        content: str,
        name: str | None = None,
    ) -> Self:
        """Add an assistant message."""
        return self.add_message(PromptRole.ASSISTANT, content, name=name)

    def add_tool(
        self,
        content: str,
        tool_call_id: str,
        name: str | None = None,
    ) -> Self:
        """Add a tool response message."""
        return self.add_message(
            PromptRole.TOOL,
            content,
            name=name,
            tool_call_id=tool_call_id,
        )

    def add_developer(self, content: str) -> Self:
        """Add a developer message."""
        return self.add_message(PromptRole.DEVELOPER, content)

    def append(self, other: Prompt) -> Self:
        """
        Append another prompt's messages to this one.

        Parameters
        ----------
        other : Prompt
            Prompt to append.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self.messages.extend(other.messages)
        self._variables.update(other._variables)
        self._touch()
        return self

    def prepend(self, other: Prompt) -> Self:
        """
        Prepend another prompt's messages to this one.

        Parameters
        ----------
        other : Prompt
            Prompt to prepend.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self.messages = other.messages + self.messages
        self._variables.update(other._variables)
        self._touch()
        return self

    def clear(self) -> Self:
        """Clear all messages and variables."""
        self.messages.clear()
        self._variables.clear()
        self.system = ""
        self._template = None
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Variable Management
    # ------------------------------------------------------------------

    def set_variable(
        self,
        name: str,
        value: Any,
        required: bool = True,
        description: str = "",
    ) -> Self:
        """
        Set a template variable.

        Parameters
        ----------
        name : str
            Variable name.
        value : Any
            Variable value.
        required : bool, default=True
            Whether the variable is required.
        description : str, default=""
            Optional description.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self._variables[name] = PromptVariable(
            name=name,
            value=value,
            required=required,
            description=description,
        )
        self._touch()
        return self

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable value.

        Parameters
        ----------
        name : str
            Variable name.
        default : Any, optional
            Default if variable doesn't exist.

        Returns
        -------
        Any
            Variable value or default.
        """

        var = self._variables.get(name)
        if var is None:
            return default
        return var.value

    def has_variable(self, name: str) -> bool:
        """Check if a variable exists."""
        return name in self._variables

    def remove_variable(self, name: str) -> Self:
        """Remove a variable."""
        self._variables.pop(name, None)
        self._touch()
        return self

    # ------------------------------------------------------------------
    # Template Management
    # ------------------------------------------------------------------

    def set_template(
        self,
        template: str,
        strict: bool | None = None,
    ) -> Self:
        """
        Set a template for the prompt.

        Parameters
        ----------
        template : str
            Template string with {variable} placeholders.
        strict : bool | None, optional
            Override strict mode for this template.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self._template = PromptTemplate(
            template=template,
            strict=strict if strict is not None else self._strict,
        )
        self._touch()
        return self

    def render(self, context: dict[str, Any] | None = None) -> str:
        """
        Render the prompt.

        If a template is set, renders the template with variables.
        Otherwise, renders the conversation.

        Parameters
        ----------
        context : dict[str, Any] | None, optional
            Additional variable values.

        Returns
        -------
        str
            Rendered prompt string.
        """

        if self._template is not None:
            render_context = {}

            for name, var in self._variables.items():
                render_context[name] = var.value

            if context:
                render_context.update(context)

            return self._template.render(render_context)

        # No template: render conversation
        return PromptRenderer.render_conversation(self.messages)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        require_user: bool = True,
        require_system: bool = False,
        max_messages: int | None = None,
        allow_unused_vars: bool = True,
    ) -> None:
        """
        Validate the prompt.

        Parameters
        ----------
        require_user : bool, default=True
            Require at least one user message.
        require_system : bool, default=False
            Require at least one system message.
        max_messages : int | None, optional
            Maximum allowed messages.
        allow_unused_vars : bool, default=True
            Allow variables that aren't used in the template.

        Raises
        ------
        ValueError
            If validation fails.
        """

        # Validate messages
        PromptValidator.validate_messages(
            self.messages,
            require_user=require_user,
            require_system=require_system,
            max_messages=max_messages,
        )

        # Validate variables
        if self._variables:
            PromptValidator.validate_variables(
                list(self._variables.values()),
                allow_unused=allow_unused_vars,
            )

    # ------------------------------------------------------------------
    # Token Estimation
    # ------------------------------------------------------------------

    def estimate_tokens(self) -> int:
        """
        Estimate the token count of the prompt.

        Uses a simple heuristic: 4 characters ≈ 1 token.
        This is a placeholder; replace with a proper tokenizer later.

        Returns
        -------
        int
            Estimated token count.
        """

        total_chars = len(self.system) + len(self.render())

        for msg in self.messages:
            total_chars += len(msg.content)

        # Rough estimate: 4 chars per token
        return (total_chars // 4) + 1

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the prompt to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """

        return PromptSerializer.to_dict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Prompt:
        """
        Deserialize a prompt from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        Prompt
            A new Prompt instance.
        """

        return PromptSerializer.from_dict(data)

    def to_json(self) -> str:
        """
        Serialize the prompt to JSON.

        Returns
        -------
        str
            JSON string.
        """

        return PromptSerializer.to_json(self)

    @classmethod
    def from_json(cls, data: str) -> Prompt:
        """
        Deserialize a prompt from JSON.

        Parameters
        ----------
        data : str
            JSON string.

        Returns
        -------
        Prompt
            A new Prompt instance.
        """

        return PromptSerializer.from_json(data)

    # ------------------------------------------------------------------
    # Clone & Merge
    # ------------------------------------------------------------------

    def clone(self) -> Prompt:
        """
        Create a deep copy of the prompt.

        Returns
        -------
        Prompt
            A new Prompt instance with the same content.
        """

        return deepcopy(self)

    def merge(self, other: Prompt) -> Self:
        """
        Merge another prompt into this one.

        Variables are merged (this takes precedence).
        Messages are extended.

        Parameters
        ----------
        other : Prompt
            Prompt to merge.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self.messages.extend(other.messages)
        self._variables.update(other._variables)

        if other.system:
            self.system = other.system

        self._touch()
        return self

    # ------------------------------------------------------------------
    # Statistics & History
    # ------------------------------------------------------------------

    def statistics(self) -> PromptStatistics:
        """
        Compute statistics for the prompt.

        Returns
        -------
        PromptStatistics
            Statistics object.
        """

        stats = PromptStatistics()
        stats.message_count = len(self.messages)
        stats.variable_count = len(self._variables)
        stats.has_template = self._template is not None

        total_chars = len(self.system)

        for msg in self.messages:
            total_chars += len(msg.content)
            if msg.role == PromptRole.SYSTEM:
                stats.system_count += 1
            elif msg.role == PromptRole.USER:
                stats.user_count += 1
            elif msg.role == PromptRole.ASSISTANT:
                stats.assistant_count += 1
            elif msg.role == PromptRole.TOOL:
                stats.tool_count += 1

        stats.total_chars = total_chars
        stats.estimated_tokens = self.estimate_tokens()

        self._statistics = stats
        return stats

    def history(self) -> PromptHistory:
        """
        Get the prompt history.

        Returns
        -------
        PromptHistory
            History object.
        """

        return self._history

    def snapshot(self) -> Self:
        """
        Save a snapshot of the current state to history.

        Returns
        -------
        Self
            The prompt instance (fluent API).
        """

        self._history.add(self)
        return self

    # ------------------------------------------------------------------
    # Integration: Convert to AIRequest
    # ------------------------------------------------------------------

    def to_request(self) -> AIRequest:
        """
        Convert the prompt to an AIRequest.

        The resulting AIRequest is ready to be passed to any provider.

        For chat providers, messages are placed in options["messages"].
        For generate providers, prompt is set to the rendered text.

        Returns
        -------
        AIRequest
            An AIRequest ready for execution.
        """

        # Render the prompt
        rendered = self.render()

        # Build messages list for chat providers
        messages = []

        if self.system:
            messages.append({"role": "system", "content": self.system})

        for msg in self.messages:
            entry = {"role": msg.role.value, "content": msg.content}
            if msg.name:
                entry["name"] = msg.name
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            messages.append(entry)

        # Create AIRequest
        request = AIRequest(
            prompt=rendered,
            input=rendered,
            options={
                "messages": messages,
            },
            task="chat",  # Default to chat
            metadata={
                "prompt_id": self.id,
                "version": self.version,
            },
        )

        return request

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self._updated_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of messages."""
        return len(self.messages)

    def __bool__(self) -> bool:
        """Return True if the prompt has any content."""
        return bool(self.system) or bool(self.messages) or bool(self._variables)

    def __str__(self) -> str:
        """Render the prompt as a string."""
        return self.render()

    def __repr__(self) -> str:
        return (
            f"Prompt(id={self.id!r}, "
            f"messages={len(self.messages)}, "
            f"variables={len(self._variables)})"
        )
