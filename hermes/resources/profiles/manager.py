"""
===============================================================================
Hermes Runtime Profile Manager
===============================================================================

Coordinates Runtime Profiles.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .loader import ProfileLoader
from .profile import RuntimeProfile
from .registry import ProfileRegistry
from .validator import ProfileValidator


class ProfileManager:
    """
    High-level Runtime Profile manager.
    """

    def __init__(self) -> None:

        self._registry = ProfileRegistry()

        self._validator = ProfileValidator()

        self._loader = ProfileLoader()

    # ------------------------------------------------------------------

    def register(
        self,
        profile: RuntimeProfile,
    ) -> None:

        self._validator.validate(profile)

        self._registry.register(profile)

    # ------------------------------------------------------------------

    def discover(
        self,
        directory: Path,
    ) -> None:

        profiles = self._loader.load(directory)

        for profile in profiles:

            self.register(profile)

    # ------------------------------------------------------------------

    def get(
        self,
        profile_id: str,
    ) -> RuntimeProfile | None:

        return self._registry.get(profile_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeProfile]:

        return self._registry.all()

    # ------------------------------------------------------------------

    def unregister(
        self,
        profile_id: str,
    ) -> None:

        self._registry.unregister(profile_id)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._registry.clear()