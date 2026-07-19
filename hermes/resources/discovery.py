"""
===============================================================================
Hermes Runtime Resource Discovery

Discovers every Runtime Resource package.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from pathlib import Path


class RuntimeResourceDiscovery:
    """
    Discovers runtime resource directories.
    """

    def discover(
        self,
        root: Path,
    ) -> list[Path]:

        directories: list[Path] = []

        if not root.exists():

            return directories

        for directory in root.iterdir():

            if directory.is_dir():

                directories.append(directory)

        return sorted(directories)
