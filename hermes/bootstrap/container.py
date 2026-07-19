"""
===============================================================================
Hermes Dependency Container

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.registry import ProviderRegistry


class HermesContainer:
    """
    Global dependency container.

    Every singleton in Hermes lives here.
    """

    def __init__(self) -> None:

        # ------------------------------------------------------------------
        # Legacy Subsystems
        # ------------------------------------------------------------------

        self.provider_registry = ProviderRegistry()

        self.provider_manager = None

        self.execution_service = None

        self.kernel_executor = None

        self.kernel_manager = None

        self.runtime_engine = None

        # ------------------------------------------------------------------
        # AI Subsystem
        # ------------------------------------------------------------------

        self.ai_registry = None

        self.ai_manager = None

        self.ai_router = None

        self.ai_pipeline = None

        self.tool_registry = None

        self.tool_manager = None

        # ------------------------------------------------------------------
        # Conversation & Sessions
        # ------------------------------------------------------------------

        self.session_manager = None

        self.conversation_prompt_builder = None

        self.request_builder = None

        # ------------------------------------------------------------------
        # Orchestrator
        # ------------------------------------------------------------------

        self.provider_selector = None

        self.response_processor = None

        self.retry_policy = None

        self.orchestrator = None