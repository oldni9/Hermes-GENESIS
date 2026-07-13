"""
===============================================================================
Hermes Runtime Policy Selector
===============================================================================
"""

from __future__ import annotations

from hermes.resources.policies.policy import RuntimePolicy


class RuntimePolicySelector:

    def select(
        self,
        policies: list[RuntimePolicy],
    ) -> RuntimePolicy | None:

        if not policies:

            return None

        policies.sort(
            key=lambda policy: policy.priority,
            reverse=True,
        )

        return policies[0]