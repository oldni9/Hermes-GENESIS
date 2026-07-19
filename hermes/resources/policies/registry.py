"""
===============================================================================
Hermes Runtime Policy Registry
===============================================================================
"""

from __future__ import annotations

from hermes.resources.policies.policy import RuntimePolicy


class RuntimePolicyRegistry:

    def __init__(self) -> None:

        self._policies: dict[str, RuntimePolicy] = {}

    # --------------------------------------------------------------

    def register(
        self,
        policy: RuntimePolicy,
    ) -> None:

        self._policies[policy.name] = policy

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimePolicy | None:

        return self._policies.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimePolicy]:

        return list(self._policies.values())

    # --------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimePolicy]:

        return [policy for policy in self._policies.values() if policy.enabled]
