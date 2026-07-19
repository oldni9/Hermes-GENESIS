"""
===============================================================================
Hermes Runtime Health
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.runtime.runtime import Runtime


@dataclass(slots=True)
class RuntimeHealth:

    healthy: bool

    message: str


class RuntimeHealthChecker:

    def check(
        self,
        runtime: Runtime,
    ) -> RuntimeHealth:

        if not runtime.state.booted:

            return RuntimeHealth(
                False,
                "Runtime not booted.",
            )

        if runtime.state.shutting_down:

            return RuntimeHealth(
                False,
                "Runtime shutting down.",
            )

        return RuntimeHealth(
            True,
            "Runtime healthy.",
        )
