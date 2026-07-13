"""
===============================================================================
Hermes Runtime Resource Loader

Loads runtime resources from disk.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
import json


class RuntimeResourceLoader:
    """
    Loads JSON runtime resources.
    """

    def load(
        self,
        path: Path,
    ) -> list[dict]:

        resources: list[dict] = []

        if not path.exists():

            return resources

        for file in path.glob("*.json"):

            with file.open(
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

            if isinstance(data, list):

                resources.extend(data)

            else:

                resources.append(data)

        return resources