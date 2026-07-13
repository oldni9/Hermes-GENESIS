"""
===============================================================================
Hermes Runtime Profile Validator
===============================================================================
"""

from __future__ import annotations

from hermes.resources.profiles.profile import RuntimeProfile


class RuntimeProfileValidator:

    def validate(
        self,
        profile: RuntimeProfile,
    ) -> None:

        if not profile.name.strip():

            raise ValueError(
                "Profile name cannot be empty."
            )