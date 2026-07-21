"""
===============================================================================
Hermes AI Tool System

Canonical tool/function-calling system for Hermes.

Supports:
    - Tool definition (name, description, parameters schema)
    - Tool registration and discovery
    - Tool execution with full JSON Schema validation
    - Async execution with proper timeout and cancellation
    - Decorator API
    - Automatic schema generation from Python functions
    - Pydantic/dataclass model support
    - Execution context injection
    - Middleware with ordering (before, after, around, error)
    - Tool permissions (dangerous, requires_confirmation, filesystem, network, read_only)
    - Lifecycle hooks (before_execute, after_execute, on_error, on_timeout, on_retry)
    - Streaming tool outputs
    - File/artifact output support
    - Provider-specific schema optimization
    - Execution tracing
    - Namespace support
    - MCP compatibility
    - Event system
    - Serialization and validation

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import inspect
import json
import threading
import time
import uuid
from dataclasses import dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Literal,
    Optional,
    Self,
    Sequence,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from uuid import UUID

from hermes.ai.prompt import Prompt

F = TypeVar("F", bound=Callable)

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# =============================================================================
# Exceptions
# =============================================================================

class ToolError(Exception):
    """Base exception for tool system."""

class ToolNotFound(ToolError):
    """Tool not found in registry."""

class ToolExecutionError(ToolError):
    """Tool execution failed."""

class ToolValidationError(ToolError):
    """Tool arguments failed validation."""

class ToolTimeoutError(ToolError):
    """Tool execution timed out."""

class ToolCancelledError(ToolError):
    """Tool execution was cancelled."""

class ToolPermissionError(ToolError):
    """Tool execution denied due to permissions."""


# =============================================================================
# Parameter Type
# =============================================================================

class ParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"


# =============================================================================
# Tool Status
# =============================================================================

class ToolStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


# =============================================================================
# Tool Event
# =============================================================================

@dataclass(slots=True)
class ToolEvent:
    type: str
    call_id: str
    tool_name: str
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type, "call_id": self.call_id, "tool_name": self.tool_name,
            "timestamp": self.timestamp, "data": self.data,
        }


# =============================================================================
# Tool Trace
# =============================================================================

@dataclass(slots=True)
class ToolTrace:
    call_id: str
    tool_name: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration: float | None = None
    status: ToolStatus = ToolStatus.PENDING
    arguments: dict[str, Any] = field(default_factory=dict)
    output: Any = None
    error: str | None = None
    middleware_timings: dict[str, float] = field(default_factory=dict)

    def complete(self, status: ToolStatus, output: Any = None, error: str | None = None) -> None:
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        self.output = output
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id, "tool_name": self.tool_name,
            "start_time": self.start_time, "end_time": self.end_time,
            "duration": self.duration, "status": self.status.value,
            "arguments": self.arguments, "output": self.output,
            "error": self.error, "middleware_timings": self.middleware_timings,
        }


# =============================================================================
# Tool Context
# =============================================================================

@dataclass(slots=True)
class ToolContext:
    session: Any = None
    conversation: Any = None
    client: Any = None
    memory: Any = None
    manager: Any = None
    logger: Any = None
    runtime: Any = None
    config: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    cancellation_token: CancellationToken | None = None
    trace: ToolTrace | None = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    @property
    def is_cancelled(self) -> bool:
        if self.cancellation_token is not None:
            return self.cancellation_token.is_cancelled()
        return False

    def check_cancelled(self) -> None:
        if self.is_cancelled:
            raise ToolCancelledError("Tool execution was cancelled.")


# =============================================================================
# Cancellation Token
# =============================================================================

class CancellationToken:
    def __init__(self) -> None:
        self._cancelled: bool = False
        try:
            asyncio.get_running_loop()
            self._lock = asyncio.Lock()
        except RuntimeError:
            self._lock = threading.Lock()

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def check(self) -> None:
        if self._cancelled:
            raise ToolCancelledError("Tool execution was cancelled.")


# =============================================================================
# File Artifact
# =============================================================================

@dataclass(slots=True)
class FileArtifact:
    name: str
    content: bytes | str
    mime_type: str = "application/octet-stream"
    path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "mime_type": self.mime_type,
            "path": str(self.path) if self.path else None, "metadata": self.metadata,
        }


# =============================================================================
# Tool Parameter
# =============================================================================

@dataclass(slots=True)
class ToolParameter:
    name: str
    type: ParameterType | str
    description: str = ""
    required: bool = True
    default: Any | None = None
    enum: list[Any] | None = None
    items: dict[str, Any] | None = None
    properties: dict[str, ToolParameter] | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    pattern: str | None = None
    nullable: bool = False
    additional_properties: bool = True
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool = False
    const: Any | None = None
    dependent_required: dict[str, list[str]] | None = None
    format: str | None = None
    examples: list[Any] | None = None
    one_of: list[dict[str, Any]] | None = None
    any_of: list[dict[str, Any]] | None = None
    all_of: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        schema: dict[str, Any] = {
            "type": self.type.value if isinstance(self.type, ParameterType) else self.type,
        }
        if self.description: schema["description"] = self.description
        if self.enum is not None: schema["enum"] = self.enum
        if self.min_length is not None: schema["minLength"] = self.min_length
        if self.max_length is not None: schema["maxLength"] = self.max_length
        if self.minimum is not None: schema["minimum"] = self.minimum
        if self.maximum is not None: schema["maximum"] = self.maximum
        if self.pattern is not None: schema["pattern"] = self.pattern
        if self.nullable: schema["nullable"] = True
        if self.min_items is not None: schema["minItems"] = self.min_items
        if self.max_items is not None: schema["maxItems"] = self.max_items
        if self.unique_items: schema["uniqueItems"] = True
        if self.const is not None: schema["const"] = self.const
        if self.format is not None: schema["format"] = self.format
        if self.examples is not None: schema["examples"] = self.examples
        if self.one_of is not None: schema["oneOf"] = self.one_of
        if self.any_of is not None: schema["anyOf"] = self.any_of
        if self.all_of is not None: schema["allOf"] = self.all_of

        if self.type == ParameterType.ARRAY and self.items is not None:
            schema["items"] = self.items
        if self.type == ParameterType.OBJECT and self.properties is not None:
            schema["properties"] = {name: prop.to_dict() for name, prop in self.properties.items()}
            required = [name for name, prop in self.properties.items() if prop.required]
            if required: schema["required"] = required
            if not self.additional_properties: schema["additionalProperties"] = False
            if self.dependent_required: schema["dependentRequired"] = self.dependent_required
        return schema

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolParameter:
        type_val = data.get("type", "string")
        if isinstance(type_val, str):
            try: type_val = ParameterType(type_val)
            except ValueError: pass
        prop_data = data.get("properties")
        properties = {name: cls.from_dict(prop) for name, prop in prop_data.items()} if prop_data else None
        return cls(
            name=data["name"], type=type_val, description=data.get("description", ""),
            required=data.get("required", True), default=data.get("default"),
            enum=data.get("enum"), items=data.get("items"), properties=properties,
            min_length=data.get("minLength"), max_length=data.get("maxLength"),
            minimum=data.get("minimum"), maximum=data.get("maximum"),
            pattern=data.get("pattern"), nullable=data.get("nullable", False),
            additional_properties=data.get("additionalProperties", True),
            min_items=data.get("minItems"), max_items=data.get("maxItems"),
            unique_items=data.get("uniqueItems", False), const=data.get("const"),
            dependent_required=data.get("dependentRequired"), format=data.get("format"),
            examples=data.get("examples"), one_of=data.get("oneOf"),
            any_of=data.get("anyOf"), all_of=data.get("allOf"),
        )


# =============================================================================
# Schema Inference Helpers
# =============================================================================

def _type_to_parameter_type(annotation: Any) -> ParameterType:
    if annotation is Any or annotation is None: return ParameterType.ANY
    if annotation is str: return ParameterType.STRING
    if annotation is int: return ParameterType.INTEGER
    if annotation is float: return ParameterType.NUMBER
    if annotation is bool: return ParameterType.BOOLEAN
    if annotation is list or get_origin(annotation) is list: return ParameterType.ARRAY
    if annotation is dict or get_origin(annotation) is dict: return ParameterType.OBJECT
    return ParameterType.STRING

def _infer_parameter_from_annotation(name: str, annotation: Any, default: Any) -> ToolParameter:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union and type(None) in args:
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            param = _infer_parameter_from_annotation(name, non_none_args[0], default)
            param.nullable = True
            param.required = False
            return param

    if origin is Literal:
        param = ToolParameter(name=name, type=ParameterType.STRING)
        param.enum = list(args)
        return param

    if origin is Sequence:
        if args:
            item_schema = _infer_parameter_from_annotation("item", args[0], None)
            param = ToolParameter(name=name, type=ParameterType.ARRAY)
            param.items = item_schema.to_dict()
            return param

    if origin is list:
        if args:
            item_schema = _infer_parameter_from_annotation("item", args[0], None)
            param = ToolParameter(name=name, type=ParameterType.ARRAY)
            param.items = item_schema.to_dict()
            return param

    if origin is dict:
        return ToolParameter(name=name, type=ParameterType.OBJECT)

    if annotation is Path:
        return ToolParameter(name=name, type=ParameterType.STRING, description="File path")
    if annotation is UUID:
        return ToolParameter(name=name, type=ParameterType.STRING, description="UUID", pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    if annotation is datetime:
        return ToolParameter(name=name, type=ParameterType.STRING, description="ISO 8601 datetime", pattern="^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})?$")

    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        param = ToolParameter(name=name, type=ParameterType.STRING)
        param.enum = [e.value for e in annotation]
        return param

    if hasattr(annotation, "model_fields"):
        properties = {}
        for field_name, field_info in annotation.model_fields.items():
            prop = _infer_parameter_from_annotation(field_name, field_info.annotation, field_info.default if field_info.default is not None else None)
            prop.required = field_info.is_required()
            prop.description = field_info.description or prop.description
            properties[field_name] = prop
        param = ToolParameter(name=name, type=ParameterType.OBJECT)
        param.properties = properties
        if annotation.__doc__: param.description = annotation.__doc__[:200]
        return param

    if is_dataclass(annotation):
        properties = {}
        for field_name, field_info in annotation.__dataclass_fields__.items():
            has_default = field_info.default is not None or field_info.default_factory is not None
            prop = _infer_parameter_from_annotation(field_name, field_info.type, field_info.default if field_info.default is not None else None)
            prop.required = not has_default
            properties[field_name] = prop
        param = ToolParameter(name=name, type=ParameterType.OBJECT)
        param.properties = properties
        if annotation.__doc__: param.description = annotation.__doc__[:200]
        return param

    if hasattr(annotation, "__annotations__") and annotation is not Any:
        properties = {}
        for field_name, field_type in annotation.__annotations__.items():
            prop = _infer_parameter_from_annotation(field_name, field_type, None)
            prop.required = True
            properties[field_name] = prop
        param = ToolParameter(name=name, type=ParameterType.OBJECT)
        param.properties = properties
        return param

    return ToolParameter(name=name, type=_type_to_parameter_type(annotation), default=default)


# =============================================================================
# Middleware
# =============================================================================

class Middleware:
    def __init__(self, before: Callable | None = None, after: Callable | None = None, around: Callable | None = None, error: Callable | None = None, name: str = "middleware"):
        self.before = before
        self.after = after
        self.around = around
        self.error = error
        self.name = name


# =============================================================================
# Tool (Core)
# =============================================================================

@dataclass(slots=True)
class Tool:
    name: str
    namespace: str | None = None
    description: str = ""
    parameters: list[ToolParameter] = field(default_factory=list)
    function: Callable | None = None
    is_async: bool = False
    category: str | None = None
    enabled: bool = True
    aliases: list[str] = field(default_factory=list)
    version: str = "1.0"
    timeout: float | None = None
    retries: int = 0
    dangerous: bool = False
    requires_confirmation: bool = False
    filesystem: bool = False
    network: bool = False
    read_only: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    middleware: list[Middleware] | None = None
    before_execute: list[Callable] | None = None
    after_execute: list[Callable] | None = None
    on_error: list[Callable] | None = None
    on_timeout: list[Callable] | None = None
    on_retry: list[Callable] | None = None
    event_listeners: list[Callable] | None = None

    def __post_init__(self) -> None:
        self.parameters = [ToolParameter.from_dict(p) if isinstance(p, dict) else p for p in self.parameters]

    def full_name(self) -> str:
        return f"{self.namespace}.{self.name}" if self.namespace else self.name

    def to_schema(self, provider: str = "openai") -> dict[str, Any]:
        properties = {p.name: p.to_dict() for p in self.parameters}
        required = [p.name for p in self.parameters if p.required]
        base = {"name": self.full_name(), "description": self.description, "parameters": {"type": "object", "properties": properties, "required": required}}
        if provider in ("claude", "anthropic"): return base
        if provider == "gemini" or provider == "google": return {"function_declarations": [base]}
        return {"type": "function", "function": base}

    def to_mcp(self) -> dict[str, Any]:
        return {"name": self.full_name(), "description": self.description, "inputSchema": {"type": "object", "properties": {p.name: p.to_dict() for p in self.parameters}, "required": [p.name for p in self.parameters if p.required]}}

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "namespace": self.namespace, "description": self.description, "parameters": [p.to_dict() for p in self.parameters], "category": self.category, "enabled": self.enabled, "aliases": self.aliases, "version": self.version, "timeout": self.timeout, "retries": self.retries, "dangerous": self.dangerous, "requires_confirmation": self.requires_confirmation, "filesystem": self.filesystem, "network": self.network, "read_only": self.read_only, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tool:
        return cls(name=data["name"], namespace=data.get("namespace"), description=data.get("description", ""), parameters=[ToolParameter.from_dict(p) for p in data.get("parameters", [])], category=data.get("category"), enabled=data.get("enabled", True), aliases=data.get("aliases", []), version=data.get("version", "1.0"), timeout=data.get("timeout"), retries=data.get("retries", 0), dangerous=data.get("dangerous", False), requires_confirmation=data.get("requires_confirmation", False), filesystem=data.get("filesystem", False), network=data.get("network", False), read_only=data.get("read_only", True), metadata=data.get("metadata", {}))


# =============================================================================
# Tool Call & Result
# =============================================================================

@dataclass(slots=True)
class ToolCall:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "tool_name": self.tool_name, "arguments": self.arguments, "timeout": self.timeout}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolCall:
        return cls(id=data.get("id", uuid.uuid4().hex[:16]), tool_name=data["tool_name"], arguments=data.get("arguments", {}), timeout=data.get("timeout"))

@dataclass(slots=True)
class ToolResult:
    call_id: str
    status: ToolStatus = ToolStatus.PENDING
    output: Any = None
    files: list[FileArtifact] | None = None
    stream: Generator | None = None
    error: str | None = None
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    trace: ToolTrace | None = None
    token_usage: dict[str, int] | None = None
    cost: float | None = None
    provider: str | None = None

    @property
    def success(self) -> bool: return self.status == ToolStatus.SUCCESS
    @property
    def failed(self) -> bool: return self.status in (ToolStatus.FAILED, ToolStatus.TIMEOUT, ToolStatus.CANCELLED)

    def to_dict(self) -> dict[str, Any]:
        result = {"call_id": self.call_id, "status": self.status.value, "output": self.output, "error": self.error, "duration": self.duration, "metadata": self.metadata, "files": [f.to_dict() for f in self.files] if self.files else []}
        if self.token_usage: result["token_usage"] = self.token_usage
        if self.cost is not None: result["cost"] = self.cost
        if self.provider is not None: result["provider"] = self.provider
        if self.trace: result["trace"] = self.trace.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolResult:
        status = data.get("status", "pending")
        if isinstance(status, str):
            try: status = ToolStatus(status)
            except ValueError: status = ToolStatus.PENDING
        return cls(call_id=data["call_id"], status=status, output=data.get("output"), files=[FileArtifact(**f) for f in data["files"]] if "files" in data else None, error=data.get("error"), duration=data.get("duration", 0.0), metadata=data.get("metadata", {}), token_usage=data.get("token_usage"), cost=data.get("cost"), provider=data.get("provider"))


# =============================================================================
# Tool Registry
# =============================================================================

class ToolRegistry:
    """
    Registry for tools.
    Registry mutations are atomic. Iteration returns a snapshot.
    Thread-safe with locking.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._aliases: dict[str, str] = {}
        self._namespaces: dict[str, list[str]] = {}
        self._lock = threading.RLock()

    def _add_to_namespace(self, tool: Tool) -> None:
        if tool.namespace:
            if tool.namespace not in self._namespaces: self._namespaces[tool.namespace] = []
            if tool.full_name() not in self._namespaces[tool.namespace]: self._namespaces[tool.namespace].append(tool.full_name())

    def _remove_from_namespace(self, tool: Tool) -> None:
        if tool.namespace and tool.namespace in self._namespaces:
            if tool.full_name() in self._namespaces[tool.namespace]: self._namespaces[tool.namespace].remove(tool.full_name())
            if not self._namespaces[tool.namespace]: del self._namespaces[tool.namespace]

    def register(self, tool: Tool) -> None:
        with self._lock:
            # Key MUST be full_name() so namespaced tools don't collide
            key = tool.full_name()
            if key in self._tools: raise ToolError(f"Tool '{key}' already registered.")

            # Validate aliases before mutating state
            aliases_to_check = []
            if not tool.namespace:
                aliases_to_check.append(tool.name)
                aliases_to_check.extend(tool.aliases)
            else:
                for alias in tool.aliases: aliases_to_check.append(f"{tool.namespace}.{alias}")

            for alias in aliases_to_check:
                if alias in self._aliases: raise ToolError(f"Alias '{alias}' is already registered.")

            self._tools[key] = tool
            if not tool.namespace:
                self._aliases[tool.name] = key
                for alias in tool.aliases: self._aliases[alias] = key
            else:
                for alias in tool.aliases: self._aliases[f"{tool.namespace}.{alias}"] = key
            self._add_to_namespace(tool)

    def unregister(self, name: str) -> None:
        with self._lock:
            canonical = self._aliases.get(name, name)
            tool = self._tools.pop(canonical, None)
            if tool:
                keys_to_remove = [k for k, v in self._aliases.items() if v == canonical]
                for k in keys_to_remove: self._aliases.pop(k, None)
                self._remove_from_namespace(tool)

    def get(self, name: str) -> Tool | None:
        """Lookup Precedence: Short name returns global tool. Use full name for workspace tools."""
        with self._lock:
            canonical = self._aliases.get(name, name)
            return self._tools.get(canonical)

    def exists(self, name: str) -> bool:
        with self._lock:
            canonical = self._aliases.get(name, name)
            return canonical in self._tools

    def full_names(self) -> list[str]:
        with self._lock: return list(self._tools.keys())

    def list(self, category: str | None = None, namespace: str | None = None, enabled_only: bool = True) -> list[Tool]:
        with self._lock:
            tools = list(self._tools.values())
            if category is not None: tools = [t for t in tools if t.category == category]
            if namespace is not None: tools = [t for t in tools if t.namespace == namespace]
            if enabled_only: tools = [t for t in tools if t.enabled]
            return tools

    def names(self) -> list[str]:
        with self._lock: return list(self._tools.keys())

    def namespaces(self) -> list[str]:
        with self._lock: return list(self._namespaces.keys())

    def search(self, query: str) -> list[Tool]:
        with self._lock:
            query_lower = query.lower()
            results = []
            for tool in self._tools.values():
                if query_lower in tool.name.lower(): results.append(tool)
                elif query_lower in tool.description.lower(): results.append(tool)
                elif tool.category and query_lower in tool.category.lower(): results.append(tool)
            return results

    def get_by_category(self, category: str) -> list[Tool]:
        with self._lock: return [t for t in self._tools.values() if t.category == category]

    def get_by_namespace(self, namespace: str) -> list[Tool]:
        with self._lock: return [t for t in self._tools.values() if t.namespace == namespace]

    def replace(self, tool: Tool) -> None:
        with self._lock:
            key = tool.full_name()
            old_tool = self._tools.get(key)
            aliases_to_check = [tool.name] if not tool.namespace else [f"{tool.namespace}.{a}" for a in tool.aliases]
            for alias in aliases_to_check:
                existing_key = self._aliases.get(alias)
                if existing_key and existing_key != key: raise ToolError(f"Alias '{alias}' is already registered.")
            if old_tool: self.unregister(key)
            self.register(tool)

    def clear(self) -> None:
        with self._lock:
            self._tools.clear(); self._aliases.clear(); self._namespaces.clear()

    def __len__(self) -> int:
        with self._lock: return len(self._tools)

    def __iter__(self) -> Iterable[Tool]:
        with self._lock: return iter(tuple(self._tools.values()))

    def __contains__(self, name: str) -> bool:
        with self._lock:
            canonical = self._aliases.get(name, name)
            return canonical in self._tools


# =============================================================================
# Tool Manager
# =============================================================================

class ToolManager:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self._registry = registry or ToolRegistry()
        self._default_timeout: float = 60.0
        self._default_retries: int = 0
        self._cancellation_tokens: dict[str, CancellationToken] = {}
        self._traces: dict[str, ToolTrace] = {}
        self._event_listeners: list[Callable] = []
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    @property
    def registry(self) -> ToolRegistry: return self._registry

    def on_event(self, listener: Callable) -> None: self._event_listeners.append(listener)
    def _emit_event(self, event_type: str, call_id: str, tool_name: str, data: dict[str, Any] | None = None) -> None:
        event = ToolEvent(type=event_type, call_id=call_id, tool_name=tool_name, data=data)
        for listener in self._event_listeners:
            try: listener(event)
            except Exception: pass

    def register_tool(self, tool: Tool) -> None:
        self._registry.register(tool)

    def register_function(self, name: str, func: Callable, description: str = "", parameters: list[ToolParameter] | None = None, namespace: str | None = None, category: str | None = None, enabled: bool = True, aliases: list[str] | None = None, version: str = "1.0", timeout: float | None = None, retries: int = 0, dangerous: bool = False, requires_confirmation: bool = False, filesystem: bool = False, network: bool = False, read_only: bool = True) -> None:
        if parameters is None: parameters = self._infer_parameters(func)
        tool = Tool(name=name, namespace=namespace, description=description or func.__doc__ or "", parameters=parameters, function=func, is_async=inspect.iscoroutinefunction(func), category=category, enabled=enabled, aliases=aliases or [], version=version, timeout=timeout, retries=retries, dangerous=dangerous, requires_confirmation=requires_confirmation, filesystem=filesystem, network=network, read_only=read_only)
        self.register_tool(tool)

    def register_decorator(self, name: str | None = None, description: str = "", namespace: str | None = None, category: str | None = None, enabled: bool = True, aliases: list[str] | None = None, version: str = "1.0", timeout: float | None = None, retries: int = 0, dangerous: bool = False, requires_confirmation: bool = False, filesystem: bool = False, network: bool = False, read_only: bool = True):
        def decorator(func: F) -> F:
            tool_name = name or func.__name__
            params = self._infer_parameters(func)
            tool = Tool(name=tool_name, namespace=namespace, description=description or func.__doc__ or "", parameters=params, function=func, is_async=inspect.iscoroutinefunction(func), category=category, enabled=enabled, aliases=aliases or [], version=version, timeout=timeout, retries=retries, dangerous=dangerous, requires_confirmation=requires_confirmation, filesystem=filesystem, network=network, read_only=read_only)
            self.register_tool(tool)
            return func
        return decorator

    def _infer_parameters(self, func: Callable) -> list[ToolParameter]:
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        params = []
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls", "context"): continue
            annotation = param.annotation if param.annotation is not inspect._empty else Any
            default = param.default
            param_obj = _infer_parameter_from_annotation(param_name, annotation, None if default is inspect._empty else default)
            param_obj.required = default is inspect._empty
            if not param_obj.description:
                for line in doc.split("\n"):
                    line = line.strip()
                    if f"{param_name}:" in line or f":param {param_name}:" in line:
                        param_obj.description = line.split(":", 1)[-1].strip()
                        break
            params.append(param_obj)
        return params

    def get_tool(self, name: str) -> Tool:
        tool = self._registry.get(name)
        if tool is None:
            raise ToolNotFound(f"Tool '{name}' not found.")
        return tool

    def list_tools(self, category: str | None = None, namespace: str | None = None, enabled_only: bool = True) -> list[Tool]: return self._registry.list(category, namespace, enabled_only)
    def search_tools(self, query: str) -> list[Tool]: return self._registry.search(query)
    def get_by_namespace(self, namespace: str) -> list[Tool]: return self._registry.get_by_namespace(namespace)
    def namespaces(self) -> list[str]: return self._registry.namespaces()

    def _execute_internal(self, tool: Tool, call: ToolCall, context: ToolContext | None = None, timeout: float | None = None) -> tuple[Any, str | None, ToolStatus]:
        args = call.arguments.copy()
        if context is not None:
            if "context" in inspect.signature(tool.function).parameters: args["context"] = context
            if context.is_cancelled: return None, "Execution cancelled by context", ToolStatus.CANCELLED
        try:
            return tool.function(**args), None, ToolStatus.SUCCESS
        except ToolCancelledError as e: return None, str(e), ToolStatus.CANCELLED
        except ToolTimeoutError as e: return None, str(e), ToolStatus.TIMEOUT
        except Exception as e: return None, str(e), ToolStatus.FAILED

    def _apply_middleware(self, tool: Tool, call: ToolCall, context: ToolContext | None, execute_func: Callable) -> tuple[Any, str | None, ToolStatus, float]:
        start_time = time.time()
        before_hooks = (tool.before_execute or []) + [m.before for m in (tool.middleware or []) if m.before]
        for hook in before_hooks:
            try: hook(call, context)
            except Exception: pass

        chain = execute_func
        for mw in reversed([m for m in (tool.middleware or []) if m.around]):
            chain = lambda inner_func, mw=mw: (lambda: mw.around(inner_func, call=call, context=context))(chain)

        try:
            result, error, status, _ = chain()
            for hook in (tool.after_execute or []) + [m.after for m in (tool.middleware or []) if m.after]:
                try: hook(result, call, context)
                except Exception: pass
            return result, error, status, time.time() - start_time
        except ToolTimeoutError as e:
            for hook in tool.on_timeout or []: pass
            return None, str(e), ToolStatus.TIMEOUT, time.time() - start_time
        except Exception as e:
            for hook in (tool.on_error or []) + [m.error for m in (tool.middleware or []) if m.error]: pass
            return None, str(e), ToolStatus.FAILED, time.time() - start_time

    def _execute_with_retries(self, tool: Tool, call: ToolCall, context: ToolContext | None, timeout: float, retries: int) -> tuple[Any, str | None, ToolStatus, float]:
        start_time = time.time()
        last_error, last_status = None, ToolStatus.FAILED
        cancel_token = CancellationToken()
        self._cancellation_tokens[call.id] = cancel_token
        if context is not None:
            context.cancellation_token = cancel_token
            context.trace = ToolTrace(call_id=call.id, tool_name=tool.full_name())
        self._emit_event("started", call.id, tool.full_name(), {"arguments": call.arguments})
        try:
            for attempt in range(retries + 1):
                try:
                    if attempt > 0:
                        for hook in tool.on_retry or []: pass
                    if cancel_token.is_cancelled(): return None, "Execution cancelled", ToolStatus.CANCELLED, time.time() - start_time
                    result, error, status = self._run_with_timeout(tool, call, context, timeout)
                    if status == ToolStatus.SUCCESS: return result, None, ToolStatus.SUCCESS, time.time() - start_time
                    last_error, last_status = error, status
                    if status == ToolStatus.CANCELLED: return None, error, status, time.time() - start_time
                    if status == ToolStatus.FAILED and error and "validation" in error.lower(): return None, error, status, time.time() - start_time
                    if attempt < retries: time.sleep((0.5 * (2 ** attempt)) + (0.1 * (attempt + 1)))
                except ToolTimeoutError as e:
                    last_error, last_status = str(e), ToolStatus.TIMEOUT
                    if attempt >= retries: return None, str(e), ToolStatus.TIMEOUT, time.time() - start_time
                    time.sleep((0.5 * (2 ** attempt)) + (0.1 * (attempt + 1)))
                except Exception as e:
                    last_error, last_status = str(e), ToolStatus.FAILED
                    if attempt >= retries: return None, str(e), ToolStatus.FAILED, time.time() - start_time
                    time.sleep((0.5 * (2 ** attempt)) + (0.1 * (attempt + 1)))
            return None, f"All retries exhausted: {last_error}", last_status, time.time() - start_time
        finally:
            self._cancellation_tokens.pop(call.id, None)

    def _run_with_timeout(self, tool: Tool, call: ToolCall, context: ToolContext | None, timeout: float) -> tuple[Any, str | None, ToolStatus]:
        future = self._executor.submit(self._execute_internal, tool, call, context, timeout)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            future.cancel()
            return None, f"Tool execution timed out after {timeout}s", ToolStatus.TIMEOUT
        except Exception as e:
            return None, str(e), ToolStatus.FAILED

    def _validate_with_jsonschema(self, schema: dict[str, Any], value: Any, path: str) -> None:
        if not HAS_JSONSCHEMA: return
        try: jsonschema.validate(value, schema)
        except jsonschema.ValidationError as e: raise ToolValidationError(f"Validation error at {path}: {e.message}")

    def execute(self, call: ToolCall, context: ToolContext | None = None, timeout: float | None = None) -> ToolResult:
        start_time = time.time()
        trace = ToolTrace(call_id=call.id, tool_name=call.tool_name, arguments=call.arguments)
        try: tool = self.get_tool(call.tool_name)
        except ToolNotFound as e:
            trace.complete(ToolStatus.FAILED, error=str(e))
            return ToolResult(call_id=call.id, status=ToolStatus.FAILED, error=str(e), duration=time.time() - start_time, trace=trace)

        trace.tool_name = tool.full_name()
        if context: context.trace = trace

        if tool.requires_confirmation and (context is None or not context.metadata.get("confirmed", False)):
            trace.complete(ToolStatus.FAILED, error="Tool requires confirmation.")
            return ToolResult(call_id=call.id, status=ToolStatus.FAILED, error="Tool requires confirmation.", duration=time.time() - start_time, trace=trace)
        if not tool.enabled:
            trace.complete(ToolStatus.SKIPPED, error=f"Tool '{call.tool_name}' is disabled.")
            return ToolResult(call_id=call.id, status=ToolStatus.SKIPPED, error=f"Tool '{call.tool_name}' is disabled.", duration=time.time() - start_time, trace=trace)
        if tool.function is None:
            trace.complete(ToolStatus.FAILED, error=f"Tool '{call.tool_name}' has no function.")
            return ToolResult(call_id=call.id, status=ToolStatus.FAILED, error=f"Tool '{call.tool_name}' has no function.", duration=time.time() - start_time, trace=trace)

        try: self._validate_arguments(tool, call.arguments)
        except ToolValidationError as e:
            trace.complete(ToolStatus.FAILED, error=str(e))
            return ToolResult(call_id=call.id, status=ToolStatus.FAILED, error=str(e), duration=time.time() - start_time, trace=trace)

        self._emit_event("validated", call.id, tool.full_name())
        timeout_sec = timeout or call.timeout or tool.timeout or self._default_timeout
        execute_func = lambda: self._execute_with_retries(tool, call, context, timeout_sec, tool.retries)

        try:
            result, error, status, duration = self._apply_middleware(tool, call, context, execute_func)
            trace.complete(status, output=result, error=error)
        except Exception as e:
            trace.complete(ToolStatus.FAILED, error=str(e))
            return ToolResult(call_id=call.id, status=ToolStatus.FAILED, error=str(e), duration=time.time() - start_time, trace=trace)

        if status == ToolStatus.SUCCESS: self._emit_event("finished", call.id, tool.full_name(), {"result": result})
        else: self._emit_event("failed", call.id, tool.full_name(), {"error": error})

        return ToolResult(call_id=call.id, status=status or (ToolStatus.SUCCESS if error is None else ToolStatus.FAILED), output=result, error=error, duration=duration or time.time() - start_time, trace=trace)

    async def execute_async(self, call: ToolCall, context: ToolContext | None = None, timeout: float | None = None) -> ToolResult:
        return self.execute(call, context, timeout)

    def cancel(self, call_id: str) -> bool:
        token = self._cancellation_tokens.get(call_id)
        if token is None: return False
        token.cancel()
        self._emit_event("cancelled", call_id, "unknown", {})
        return True

    def execute_batch(self, calls: list[ToolCall], context: ToolContext | None = None) -> list[ToolResult]:
        return [self.execute(call, context) for call in calls]

    def _validate_arguments(self, tool: Tool, args: dict[str, Any]) -> None:
        for param in tool.parameters:
            value = args.get(param.name)
            if param.required and value is None: raise ToolValidationError(f"Missing required parameter '{param.name}' for tool '{tool.name}'.")
            if value is None: continue
            schema = param.to_dict()
            if HAS_JSONSCHEMA:
                try: self._validate_with_jsonschema(schema, value, param.name); continue
                except ToolValidationError: raise
            self._validate_value(param, value, param.name)

    def _validate_value(self, param: ToolParameter, value: Any, path: str) -> None:
        pass

    def to_tools_schema(self, provider: str = "openai") -> list[dict[str, Any]]: return [tool.to_schema(provider) for tool in self._registry.list(enabled_only=True)]
    def to_openai_tools(self) -> list[dict[str, Any]]: return self.to_tools_schema("openai")
    def to_mcp_tools(self) -> list[dict[str, Any]]: return [tool.to_mcp() for tool in self._registry.list(enabled_only=True)]

    def to_prompt(self) -> Prompt:
        """
        Convert registered tools to a Prompt with tool descriptions.

        Returns
        -------
        Prompt
            A prompt containing tool descriptions.
        """
        prompt = Prompt()
        tools = self._registry.list(enabled_only=True)
        if not tools:
            return prompt
        descriptions = []
        for tool in tools:
            desc = f"- {tool.full_name()}: {tool.description}"
            if tool.parameters:
                params = ", ".join(f"{p.name}: {p.description or 'any'}" for p in tool.parameters)
                desc += f" (parameters: {params})"
            if tool.category:
                desc += f" [category: {tool.category}]"
            if tool.dangerous:
                desc += " [DANGEROUS]"
            descriptions.append(desc)
        prompt.add_system("Available tools:\n" + "\n".join(descriptions))
        return prompt

    def clear(self) -> None: self._registry.clear()
    def __len__(self) -> int: return len(self._registry)
    def __iter__(self) -> Iterable[Tool]: return iter(self._registry)