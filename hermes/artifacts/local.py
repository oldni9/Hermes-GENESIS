"""
===============================================================================
Local Artifact Registry
===============================================================================

Dependencies:
    - typing
    - hermes.artifacts.base

Consumes:
    - ArtifactRequest

Produces:
    - LocalArtifactRegistry

Public API:
    - LocalArtifactRegistry

Note:
This implementation stores metadata in memory. Future implementations may
use SQLite or other persistent backends.
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional

from hermes.artifacts.base import Artifact, ArtifactRegistry, ArtifactRequest, ArtifactType


class LocalArtifactRegistry(ArtifactRegistry):
    """
    In-memory implementation of the ArtifactRegistry.
    """
    
    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    def register(self, request: ArtifactRequest) -> Artifact:
        # Use the factory method to centralize ID generation
        artifact = Artifact.create(request)
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def get(self, artifact_id: str) -> Optional[Artifact]:
        return self._artifacts.get(artifact_id)

    def list(self, workspace_id: str, artifact_type: Optional[ArtifactType] = None) -> List[Artifact]:
        results = [
            art for art in self._artifacts.values() 
            if art.workspace_id == workspace_id
        ]
        if artifact_type:
            results = [art for art in results if art.artifact_type == artifact_type]
            
        # Return a deterministic sorted copy
        return list(sorted(results, key=lambda a: a.created_at))

    def delete(self, artifact_id: str) -> bool:
        return self._artifacts.pop(artifact_id, None) is not None