"""
===============================================================================
Hermes Runtime Profile Selector
===============================================================================
"""

from __future__ import annotations

from hermes.resources.profiles.profile import RuntimeProfile


class RuntimeProfileSelector:

    def select(
        self,
        profiles: list[RuntimeProfile],
    ) -> RuntimeProfile | None:

        if not profiles:

            return None

        profiles.sort(
            key=lambda profile: profile.name,
        )

        return profiles[0]