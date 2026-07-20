"""
===============================================================================
Tests for Local Artifact Registry
===============================================================================
"""

import pytest
from hermes.artifacts import (
    LocalArtifactRegistry, ArtifactRegistry, 
    ArtifactRequest, ArtifactType, Artifact
)


@pytest.fixture
def registry():
    return LocalArtifactRegistry()

@pytest.fixture
def request_1():
    return ArtifactRequest(
        workspace_id="ws_123",
        execution_id="exec_456",
        name="report.md",
        artifact_type=ArtifactType.REPORT,
        path="outputs/report.md",
        metadata={"author": "agent"}
    )

def test_registry_implements_protocol(registry):
    """Verify that LocalArtifactRegistry is recognized as an ArtifactRegistry."""
    assert isinstance(registry, ArtifactRegistry)

def test_register_artifact(registry, request_1):
    """Test registering a new artifact."""
    artifact = registry.register(request_1)
    
    assert isinstance(artifact, Artifact)
    assert artifact.artifact_id.startswith("art_")
    assert artifact.workspace_id == "ws_123"
    assert artifact.execution_id == "exec_456"
    assert artifact.name == "report.md"
    assert artifact.artifact_type == ArtifactType.REPORT
    assert artifact.path == "outputs/report.md"
    assert artifact.metadata == {"author": "agent"}
    assert artifact.created_at > 0

def test_get_artifact(registry, request_1):
    """Test retrieving an artifact by ID."""
    registered = registry.register(request_1)
    fetched = registry.get(registered.artifact_id)
    
    assert fetched is not None
    assert fetched.artifact_id == registered.artifact_id

def test_get_nonexistent_artifact(registry):
    """Test that getting a non-existent artifact returns None."""
    assert registry.get("art_nonexistent") is None

def test_list_artifacts(registry, request_1):
    """Test listing artifacts for a workspace."""
    registry.register(request_1)
    
    req_2 = ArtifactRequest(
        workspace_id="ws_123",
        execution_id="exec_789",
        name="plot.png",
        artifact_type=ArtifactType.IMAGE,
        path="outputs/plot.png"
    )
    registry.register(req_2)
    
    req_3 = ArtifactRequest(
        workspace_id="ws_other",
        execution_id="exec_000",
        name="data.csv",
        artifact_type=ArtifactType.CSV,
        path="data.csv"
    )
    registry.register(req_3)
    
    # List all for ws_123
    arts = registry.list("ws_123")
    assert len(arts) == 2
    
    # List only images for ws_123
    images = registry.list("ws_123", artifact_type=ArtifactType.IMAGE)
    assert len(images) == 1
    assert images[0].name == "plot.png"

def test_delete_artifact(registry, request_1):
    """Test deleting an artifact."""
    artifact = registry.register(request_1)
    
    assert registry.delete(artifact.artifact_id) is True
    assert registry.get(artifact.artifact_id) is None
    
    # Deleting again should return False
    assert registry.delete(artifact.artifact_id) is False

def test_artifact_immutability(registry, request_1):
    """Test that artifact metadata is immutable."""
    artifact = registry.register(request_1)
    with pytest.raises(Exception):
        artifact.name = "new_name"

def test_list_empty(registry):
    """Test listing artifacts for a workspace with no artifacts."""
    arts = registry.list("ws_empty")
    assert arts == []

def test_delete_unknown(registry):
    """Test deleting a non-existent artifact returns False."""
    assert registry.delete("art_unknown") is False

def test_register_multiple_same_name(registry, request_1):
    """Test that multiple artifacts with the same name and path can be registered."""
    art1 = registry.register(request_1)
    art2 = registry.register(request_1)
    
    assert art1.artifact_id != art2.artifact_id
    assert len(registry.list("ws_123")) == 2