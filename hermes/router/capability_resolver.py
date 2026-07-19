"""
===============================================================================
Hermes Capability Resolver

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel.kernel_task import KernelTask

from hermes.router.capability import ModelCapability


class CapabilityResolver:
    """
    Determines which capability a task requires.
    """

    def resolve(
        self,
        task: KernelTask,
    ) -> ModelCapability:

        # Placeholder logic for now.
        # Later this becomes intelligent.

        return ModelCapability.CHAT
