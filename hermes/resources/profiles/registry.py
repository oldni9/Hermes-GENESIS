"""
===============================================================================
Hermes Runtime Profile Registry
===============================================================================
"""

from __future__ import annotations

from hermes.resources.profiles.profile import RuntimeProfile


class RuntimeProfileRegistry:

    def __init__(self) -> None:

        self._profiles: dict[str, RuntimeProfile] = {}

    # --------------------------------------------------------------

    def register(
        self,
        profile: RuntimeProfile,
    ) -> None:

        self._profiles[profile.name] = profile

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimeProfile | None:

        return self._profiles.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeProfile]:

        return list(self._profiles.values())

    # --------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeProfile]:

        return [profile for profile in self._profiles.values() if profile.enabled]
