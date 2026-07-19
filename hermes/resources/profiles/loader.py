"""
===============================================================================
Hermes Runtime Profile Loader
===============================================================================

Loads Runtime Profiles.

JSON loading will be implemented after the Runtime Object
schema is finalized.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .profile import RuntimeProfile


class ProfileLoader:
    """
    Loads Runtime Profiles.
    """

    def load(
        self,
        directory: Path,
    ) -> list[RuntimeProfile]:

        return []
