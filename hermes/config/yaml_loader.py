"""
===============================================================================
Hermes YAML Loader
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import yaml


class YAMLLoader:

    def load(
        self,
        path: str | Path,
    ) -> dict:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return yaml.safe_load(
                f,
            )
