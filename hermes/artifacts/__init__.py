"""
===============================================================================
Artifacts Package
===============================================================================

Dependencies:
    - hermes.artifacts.base
    - hermes.artifacts.local

Consumes:
    - None directly (re-exports)

Produces:
    - ArtifactType
    - ArtifactRequest
    - Artifact
    - ArtifactRegistry
    - LocalArtifactRegistry

Public API:
    - LocalArtifactRegistry
===============================================================================
"""

from hermes.artifacts.base import ArtifactType, ArtifactRequest, Artifact, ArtifactRegistry
from hermes.artifacts.local import LocalArtifactRegistry

__all__ = [
    "ArtifactType",
    "ArtifactRequest",
    "Artifact",
    "ArtifactRegistry",
    "LocalArtifactRegistry",
]