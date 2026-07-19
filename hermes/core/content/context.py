"""
===============================================================================
Hermes Execution Context
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.ai.conversation import AIConversation
    from hermes.memory.backend import MemoryBackend
    from hermes.services.manager import ServiceManager
    from hermes.workflow.workflow import Workflow
    from hermes.agent.runtime import AgentRuntime
    from hermes.observability.trace import ExecutionTrace

@dataclass(slots=True)
class ExecutionContext:
    """
    Shared runtime state container.
    All fields are optional; they are set as execution progresses.
    """
    configuration: Dict[str, Any] = field(default_factory=dict)
    conversation: Optional[AIConversation] = None
    memory: Optional[MemoryBackend] = None
    services: Optional[ServiceManager] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    workflow: Optional[Workflow] = None
    agent: Optional[AgentRuntime] = None
    trace: Optional[ExecutionTrace] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> ExecutionContext:
        """Deep copy with special handling for objects that implement .clone()."""
        def clone_if_possible(obj):
            if obj is None:
                return None
            if hasattr(obj, "clone") and callable(obj.clone):
                return obj.clone()
            return obj

        return ExecutionContext(
            configuration=self._deep_copy_dict(self.configuration),
            conversation=clone_if_possible(self.conversation),
            memory=clone_if_possible(self.memory),
            services=clone_if_possible(self.services),
            provider=self.provider,
            model=self.model,
            workflow=clone_if_possible(self.workflow),
            agent=clone_if_possible(self.agent),
            trace=clone_if_possible(self.trace),
            variables=self._deep_copy_dict(self.variables),
            artifacts=self._deep_copy_dict(self.artifacts),
            metadata=self._deep_copy_dict(self.metadata),
        )

    def copy(self) -> ExecutionContext:
        return self.clone()

    def _deep_copy_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively copy a dictionary (simple objects)."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deep_copy_dict(v)
            elif isinstance(v, list):
                result[k] = [self._deep_copy_dict_item(item) for item in v]
            elif isinstance(v, tuple):
                result[k] = tuple(self._deep_copy_dict_item(item) for item in v)
            elif isinstance(v, set):
                result[k] = {self._deep_copy_dict_item(item) for item in v}
            else:
                result[k] = v
        return result

    def _deep_copy_dict_item(self, item: Any) -> Any:
        if isinstance(item, dict):
            return self._deep_copy_dict(item)
        if isinstance(item, list):
            return [self._deep_copy_dict_item(subitem) for subitem in item]
        if isinstance(item, tuple):
            return tuple(self._deep_copy_dict_item(subitem) for subitem in item)
        if isinstance(item, set):
            return {self._deep_copy_dict_item(subitem) for subitem in item}
        return item

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configuration": self.configuration,
            "conversation": self.conversation,
            "memory": self.memory,
            "services": self.services,
            "provider": self.provider,
            "model": self.model,
            "workflow": self.workflow,
            "agent": self.agent,
            "trace": self.trace,
            "variables": self.variables,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionContext:
        return cls(
            configuration=data.get("configuration", {}),
            conversation=data.get("conversation"),
            memory=data.get("memory"),
            services=data.get("services"),
            provider=data.get("provider"),
            model=data.get("model"),
            workflow=data.get("workflow"),
            agent=data.get("agent"),
            trace=data.get("trace"),
            variables=data.get("variables", {}),
            artifacts=data.get("artifacts", {}),
            metadata=data.get("metadata", {}),
        )