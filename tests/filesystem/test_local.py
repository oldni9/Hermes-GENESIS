"""
===============================================================================
Tests for Local Filesystem
===============================================================================
"""

import pytest
import tempfile
import os

from hermes.filesystem import LocalFilesystem, Filesystem, FilesystemError


@pytest.fixture
def fs():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield LocalFilesystem(tmpdir)

def test_filesystem_implements_protocol(fs):
    """Verify that LocalFilesystem is recognized as a Filesystem."""
    assert isinstance(fs, Filesystem)

def test_write_and_read(fs):
    """Test writing and reading a file."""
    fs.write("outputs/report.md", "# Hello World")
    assert fs.read("outputs/report.md") == "# Hello World"
    assert fs.exists("outputs/report.md")

def test_write_overwrites(fs):
    """Test that writing to an existing path overwrites it."""
    fs.write("data.txt", "version 1")
    fs.write("data.txt", "version 2")
    assert fs.read("data.txt") == "version 2"

def test_read_nonexistent(fs):
    """Test that reading a non-existent file raises an error."""
    with pytest.raises(FilesystemError, match="File not found"):
        fs.read("missing.txt")

def test_delete_file(fs):
    """Test deleting a file."""
    fs.write("temp.txt", "delete me")
    fs.delete("temp.txt")
    assert not fs.exists("temp.txt")

def test_delete_nonexistent(fs):
    """Test that deleting a non-existent file raises an error."""
    with pytest.raises(FilesystemError, match="Path not found"):
        fs.delete("missing.txt")

def test_mkdir_and_list_files(fs):
    """Test creating directories and listing contents."""
    fs.mkdir("src/components")
    fs.write("src/components/Button.tsx", "// button")
    fs.write("src/index.tsx", "// index")
    
    files = fs.list_files("src")
    assert len(files) == 2
    names = [f.name for f in files]
    assert "components" in names
    assert "index.tsx" in names
    
    files = fs.list_files("src/components")
    assert len(files) == 1
    assert files[0].name == "Button.tsx"
    assert files[0].is_dir is False

def test_path_traversal_prevention(fs):
    """Test that path traversal (../../) is blocked."""
    fs.write("safe.txt", "safe")
    
    # Attempt traversal
    with pytest.raises(FilesystemError, match="Path traversal detected"):
        fs.read("../../../../etc/passwd")
        
    with pytest.raises(FilesystemError, match="Path traversal detected"):
        fs.write("../../evil.txt", "evil")

def test_absolute_path_rejection(fs):
    """Test that absolute paths are explicitly rejected."""
    with pytest.raises(FilesystemError, match="Absolute paths are not allowed"):
        fs.read("/etc/passwd")

def test_nested_traversal_rejection(fs):
    """Test that nested path traversal is blocked."""
    fs.mkdir("a/b")
    with pytest.raises(FilesystemError, match="Path traversal detected"):
        fs.read("a/b/../../../evil")

def test_empty_path_rejected(fs):
    """Test that empty paths are rejected."""
    with pytest.raises(FilesystemError, match="Path cannot be empty"):
        fs.read("")

def test_list_files_sorted(fs):
    """Test that list_files returns sorted results for determinism."""
    fs.write("z_file.txt", "z")
    fs.write("a_file.txt", "a")
    fs.write("m_file.txt", "m")
    
    files = fs.list_files(".")
    names = [f.name for f in files]
    assert names == sorted(names)