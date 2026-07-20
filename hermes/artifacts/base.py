"""
===============================================================================
Artifact Base
===============================================================================

Dependencies:
    - dataclasses
    - enum
    - typing
    - time
    - uuid

Consumes:
    - None

Produces:
    - ArtifactType
    - ArtifactRequest
    - Artifact
    - ArtifactRegistry

Public API:
    - ArtifactRegistry
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
import time
import uuid


class ArtifactType(str, Enum):
    """Supported artifact types."""
    IMAGE = "image"
    CSV = "csv"
    CODE = "code"
    TEXT = "text"
    NOTEBOOK = "notebook"
    REPORT = "report"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ArtifactRequest:
    """
    Immutable request to register an artifact.
    """
    workspace_id: str
    execution_id: str
    name: str
    artifact_type: ArtifactType
    path: str  # Relative path within the workspace filesystem
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Artifact:
    """
    Immutable artifact metadata record.
    """
    artifact_id: str
    workspace_id: str
    execution_id: str
    name: str
    artifact_type: ArtifactType
    path: str
    metadata: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, request: ArtifactRequest) -> "Artifact":
        """
        Factory method to create a new Artifact.
        Centralizes identity generation so that future registry implementations
        (SQLite, Remote, etc.) can use different ID strategies (ULID, Snowflake, etc.)
        without modifying the registries themselves.
        """
        artifact_id = f"art_{uuid.uuid4().hex}"
        return cls(
            artifact_id=artifact_id,
            workspace_id=request.workspace_id,
            execution_id=request.execution_id,
            name=request.name,
            artifact_type=request.artifact_type,
            path=request.path,
            metadata=request.metadata
        )


@runtime_checkable
class ArtifactRegistry(Protocol):
    """
    Protocol for artifact registry implementations.
    Manages artifact metadata. Does not handle file I/O directly.
    
    Note: The registry assumes that any paths provided in ArtifactRequest
    have already been validated and secured by the Filesystem layer.
    """
    def register(self, request: ArtifactRequest) -> Artifact:
        ...
        
    def get(self, artifact_id: str) -> Optional[Artifact]:
        ...
        
    def list(self, workspace_id: str, artifact_type: Optional[ArtifactType] = None) -> List[Artifact]:
        ...
        
    def delete(self, artifact_id: str) -> bool:
        ...