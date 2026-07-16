"""
===============================================================================
Hermes File Safety Policy
===============================================================================
"""

from __future__ import annotations

from pathlib import Path


class FileSafety:

    """
    Safety policy before executing file operations.
    """

    # ------------------------------------------------------------------

    def exists(
        self,
        path: str,
    ) -> bool:

        return Path(path).exists()

    # ------------------------------------------------------------------

    def writable(
        self,
        path: str,
    ) -> bool:

        p = Path(path)

        if not p.exists():
            return False

        try:

            with p.open("a"):
                pass

            return True

        except Exception:

            return False

    # ------------------------------------------------------------------

    def can_delete(
        self,
        path: str,
    ) -> bool:

        return self.exists(path)

    # ------------------------------------------------------------------

    def can_copy(
        self,
        source: str,
    ) -> bool:

        return self.exists(source)

    # ------------------------------------------------------------------

    def can_move(
        self,
        source: str,
    ) -> bool:

        return self.exists(source)