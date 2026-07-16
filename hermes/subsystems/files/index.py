"""
===============================================================================
Hermes File Index
===============================================================================
"""

from __future__ import annotations

from pathlib import Path


class FileIndex:

    """
    Lightweight in-memory file index.

    Later this will become SQLite-backed.
    """

    def __init__(self) -> None:

        self._files: dict[str, Path] = {}

    # ------------------------------------------------------------------

    def clear(self) -> None:

        self._files.clear()

    # ------------------------------------------------------------------

    def add(

        self,

        path: Path,

    ) -> None:

        self._files[str(path.resolve())] = path.resolve()

    # ------------------------------------------------------------------

    def build(

        self,

        root: str,

    ) -> int:

        self.clear()

        for file in Path(root).rglob("*"):

            if file.is_file():

                self.add(file)

        return len(self._files)

    # ------------------------------------------------------------------

    def all(self) -> list[Path]:

        return list(self._files.values())

    # ------------------------------------------------------------------

    def search(

        self,

        text: str,

    ) -> list[Path]:

        text = text.lower()

        return [

            p

            for p in self._files.values()

            if text in p.name.lower()

        ]

    # ------------------------------------------------------------------

    def count(self) -> int:

        return len(self._files)