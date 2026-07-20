"""
===============================================================================
Local Filesystem
===============================================================================

Dependencies:
    - os
    - pathlib
    - typing
    - hermes.filesystem.base

Consumes:
    - None

Produces:
    - LocalFilesystem

Public API:
    - LocalFilesystem

TODO:
- move()
- rename()
- copy()
- touch()
- read_bytes()
- write_bytes()
- stat()
- delete_tree()
- glob()
- watch()
- symlink policy
- Introduce a WorkspacePath abstraction instead of raw strings.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from hermes.filesystem.base import FileInfo, Filesystem, FilesystemError


class LocalFilesystem(Filesystem):
    """
    Filesystem implementation scoped to a local directory.
    Enforces relative paths and prevents path traversal.
    """
    
    def __init__(self, root_path: str) -> None:
        self._root = Path(root_path).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve a relative path against the root and prevent traversal."""
        if not relative_path:
            raise FilesystemError("Path cannot be empty.")
            
        # FIX: Explicitly reject absolute paths on all OSes
        # Path.is_absolute() is False for "/etc" on Windows, so we check manually.
        if relative_path.startswith(("/", "\\")) or (len(relative_path) > 1 and relative_path[1] == ":"):
            raise FilesystemError(f"Absolute paths are not allowed: {relative_path}")
            
        candidate = Path(relative_path)
        
        # Resolve the path. Pathlib handles `..` safely.
        target = (self._root / candidate).resolve()
        
        # Security Check: Ensure the resolved path is inside the root
        if self._root not in target.parents and target != self._root:
            raise FilesystemError(f"Path traversal detected: {relative_path}")
            
        return target

    def read(self, path: str) -> str:
        target = self._resolve_path(path)
        if not target.exists() or not target.is_file():
            raise FilesystemError(f"File not found: {path}")
        return target.read_text(encoding="utf-8")

    def write(self, path: str, content: str) -> None:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def delete(self, path: str) -> None:
        """
        Delete a file or directory.
        Directory deletion is intentionally non-recursive.
        Future: delete_tree(...)
        """
        target = self._resolve_path(path)
        if not target.exists():
            raise FilesystemError(f"Path not found: {path}")
        if target.is_dir():
            target.rmdir()  # Only removes empty directories
        else:
            target.unlink()

    def exists(self, path: str) -> bool:
        target = self._resolve_path(path)
        return target.exists()

    def mkdir(self, path: str) -> None:
        target = self._resolve_path(path)
        target.mkdir(parents=True, exist_ok=True)

    def list_files(self, path: str = ".") -> List[FileInfo]:
        target = self._resolve_path(path)
        if not target.exists() or not target.is_dir():
            raise FilesystemError(f"Directory not found: {path}")
            
        results: List[FileInfo] = []
        # Sort items for deterministic order across operating systems
        for item in sorted(target.iterdir()):
            rel_path = str(item.relative_to(self._root)).replace("\\", "/")
            results.append(FileInfo(
                path=rel_path,
                name=item.name,
                is_dir=item.is_dir(),
                size=item.stat().st_size if item.is_file() else 0
            ))
        return results