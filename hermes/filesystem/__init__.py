"""
===============================================================================
Filesystem Package
===============================================================================

Dependencies:
    - hermes.filesystem.base
    - hermes.filesystem.local

Consumes:
    - None directly (re-exports)

Produces:
    - FilesystemError
    - FileInfo
    - Filesystem
    - LocalFilesystem

Public API:
    - LocalFilesystem
===============================================================================
"""

from hermes.filesystem.base import FilesystemError, FileInfo, Filesystem
from hermes.filesystem.local import LocalFilesystem

__all__ = [
    "FilesystemError",
    "FileInfo",
    "Filesystem",
    "LocalFilesystem",
]