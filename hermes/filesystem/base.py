"""
===============================================================================
Filesystem Base
===============================================================================

Dependencies:
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - FilesystemError
    - FileInfo
    - Filesystem

Public API:
    - Filesystem
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, runtime_checkable


class FilesystemError(Exception):
    """Base exception for filesystem errors."""
    pass


@dataclass(frozen=True)
class FileInfo:
    """
    Immutable metadata about a file or directory.
    """
    path: str
    name: str
    is_dir: bool
    size: int


@runtime_checkable
class Filesystem(Protocol):
    """
    Protocol for workspace-scoped filesystem implementations.
    All paths must be relative to the workspace root.
    """
    def read(self, path: str) -> str:
        ...
        
    def write(self, path: str, content: str) -> None:
        ...
        
    def delete(self, path: str) -> None:
        ...
        
    def exists(self, path: str) -> bool:
        ...
        
    def mkdir(self, path: str) -> None:
        ...
        
    def list_files(self, path: str = ".") -> List[FileInfo]:
        ...