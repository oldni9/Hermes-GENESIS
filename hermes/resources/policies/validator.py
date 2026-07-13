"""
===============================================================================
Hermes Runtime Policy Validator
===============================================================================
"""

from __future__ import annotations

from hermes.resources.policies.policy import RuntimePolicy


class RuntimePolicyValidator:

    def validate(
        self,
        policy: RuntimePolicy,
    ) -> None:

        if not policy.name.strip():

            raise ValueError(
                "Policy name cannot be empty."
            )