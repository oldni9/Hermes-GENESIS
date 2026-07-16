"""
===============================================================================
Hermes File Metadata Service
===============================================================================
"""

from __future__ import annotations

import hashlib
import mimetypes

from pathlib import Path


class FileMetadata:

    # ---------------------------------------------------------

    def info(
        self,
        path: str,
    ) -> dict:

        p = Path(path)

        stat = p.stat()

        return {

            "name": p.name,

            "path": str(p.resolve()),

            "exists": p.exists(),

            "is_file": p.is_file(),

            "is_directory": p.is_dir(),

            "extension": p.suffix,

            "size": stat.st_size,

            "created": stat.st_ctime,

            "modified": stat.st_mtime,

            "mime": mimetypes.guess_type(p)[0],

        }

    # ---------------------------------------------------------

    def sha256(
        self,
        path: str,
    ) -> str:

        h = hashlib.sha256()

        with open(path, "rb") as f:

            while chunk := f.read(8192):

                h.update(chunk)

        return h.hexdigest()

    # ---------------------------------------------------------

    def size(
        self,
        path: str,
    ) -> int:

        return Path(path).stat().st_size