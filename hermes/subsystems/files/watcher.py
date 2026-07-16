"""
===============================================================================
Hermes File Watcher
===============================================================================
"""

from __future__ import annotations

from pathlib import Path


class FileWatcher:

    """
    Placeholder watcher.

    Future:
        watchdog
        watchfiles
        native Windows notifications
    """

    def __init__(self) -> None:

        self._paths: set[Path] = set()

    # ---------------------------------------------------------

    def watch(

        self,

        path: str,

    ) -> None:

        self._paths.add(

            Path(path).resolve()

        )

    # ---------------------------------------------------------

    def unwatch(

        self,

        path: str,

    ) -> None:

        self._paths.discard(

            Path(path).resolve()

        )

    # ---------------------------------------------------------

    def watched(self) -> list[Path]:

        return sorted(

            self._paths,

            key=str,

        )

    # ---------------------------------------------------------

    def count(self) -> int:

        return len(self._paths)