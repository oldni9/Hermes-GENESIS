"""
===============================================================================
Hermes Bootstrap

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.bootstrap.container import HermesContainer

from hermes.providers.manager import ProviderManager

from hermes.execution.service import ExecutionService

from hermes.kernel.executor import KernelExecutor

from hermes.runtime.engine import RuntimeEngine


class HermesBootstrap:

    def build(
        self,
    ) -> HermesContainer:

        container = HermesContainer()

        # --------------------------------------------------------------
        # Provider Layer
        # --------------------------------------------------------------

        container.provider_manager = ProviderManager(
            container.provider_registry,
        )

        # --------------------------------------------------------------
        # Execution Layer
        # --------------------------------------------------------------

        container.execution_service = ExecutionService(
            container.provider_manager,
        )

        # --------------------------------------------------------------
        # Kernel Layer
        # --------------------------------------------------------------

        container.kernel_executor = KernelExecutor(
            container.execution_service,
        )

        # --------------------------------------------------------------
        # Runtime Layer
        # --------------------------------------------------------------

        container.runtime_engine = RuntimeEngine(
            container.execution_service,
        )

        return container