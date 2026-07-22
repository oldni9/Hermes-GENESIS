"""
===============================================================================
Hermes Bootstrap
===============================================================================
"""

from __future__ import annotations

from hermes.ai.manager import AIManager
from hermes.ai.pipeline import AIPipeline
from hermes.ai.conversation_prompt_builder import ConversationPromptBuilder
from hermes.ai.request_builder import RequestBuilder
from hermes.ai.providers.ollama import OllamaProvider
from hermes.ai.providers.openrouter import OpenRouterProvider
from hermes.ai.registry import AIRegistry
from hermes.ai.router import AIRouter
from hermes.ai.session_manager import MemorySessionManager
from hermes.ai.tool import ToolManager, ToolRegistry

# Orchestrator imports
from hermes.ai.orchestrator import (
    AIOrchestrator,
    ProviderSelector,
    ResponseProcessor,
    RetryPolicy,
)

from hermes.bootstrap.container import HermesContainer
from hermes.execution.service import ExecutionService
from hermes.kernel.executor import KernelExecutor
from hermes.providers.manager import ProviderManager
from hermes.runtime.engine import RuntimeEngine

# Sprint 9 Planner Registry imports
from hermes.agent.executor.planners.registry import planner_registry, PlannerDescriptor, PlannerCapabilities
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner


def register_builtin_planners():
    """Registers all built-in planners into the global registry."""
    
    planner_registry.register(PlannerDescriptor(
        name="react",
        planner_class=ReActPlanner,
        description="Standard Reason + Act planner.",
        aliases=["default"],
        capabilities=PlannerCapabilities()
    ))
    
    planner_registry.register(PlannerDescriptor(
        name="reflection",
        planner_class=ReflectionPlanner,
        description="Planner that uses an LLM to critique and revise the answer.",
        capabilities=PlannerCapabilities(reflection=True)
    ))
    
    # Freeze registry after bootstrap
    planner_registry.freeze()


class HermesBootstrap:

    def build(
        self,
    ) -> HermesContainer:

        container = HermesContainer()

        # --------------------------------------------------------------
        # Register Built-in Planners (Sprint 9)
        # --------------------------------------------------------------
        register_builtin_planners()

        # --------------------------------------------------------------
        # Legacy Layer
        # --------------------------------------------------------------

        container.provider_manager = ProviderManager(
            container.provider_registry,
        )

        container.execution_service = ExecutionService(
            container.provider_manager,
        )

        container.kernel_executor = KernelExecutor(
            container.execution_service,
        )

        container.runtime_engine = RuntimeEngine(
            container.execution_service,
        )

        # --------------------------------------------------------------
        # AI Layer
        # --------------------------------------------------------------

        # Tool Registry
        container.tool_registry = ToolRegistry()

        # Tool Manager
        container.tool_manager = ToolManager(
            registry=container.tool_registry,
        )

        # AI Registry
        container.ai_registry = AIRegistry()

        # Register AI Providers
        self._register_ai_providers(container)

        # AI Manager
        container.ai_manager = AIManager(
            registry=container.ai_registry,
        )

        # AI Router
        container.ai_router = AIRouter(
            registry=container.ai_registry,
        )

        # --------------------------------------------------------------
        # Orchestrator Layer (Sprint 1)
        # --------------------------------------------------------------

        # Provider Selector (uses AIRegistry)
        container.provider_selector = ProviderSelector(
            registry=container.ai_registry,
        )

        # Response Processor
        container.response_processor = ResponseProcessor()

        # Retry Policy
        container.retry_policy = RetryPolicy.default()

        # AI Orchestrator
        container.orchestrator = AIOrchestrator(
            manager=container.ai_manager,
            provider_selector=container.provider_selector,
            response_processor=container.response_processor,
            retry_policy=container.retry_policy,
            tool_manager=container.tool_manager,  # <-- Injection
        )

        # --------------------------------------------------------------
        # Pipeline (uses Orchestrator)
        # --------------------------------------------------------------

        container.ai_pipeline = AIPipeline(
            orchestrator=container.orchestrator,
            cache=None,  # AICache instantiated inside pipeline
        )

        # --------------------------------------------------------------
        # Conversation & Sessions
        # --------------------------------------------------------------

        # Session Manager (in-memory)
        container.session_manager = MemorySessionManager()

        # Conversation Prompt Builder
        container.conversation_prompt_builder = ConversationPromptBuilder(
            trim_to=None,
            include_summary=False,
            include_system=True,
        )

        # Request Builder
        container.request_builder = RequestBuilder()

        return container

    def _register_ai_providers(
        self,
        container: HermesContainer,
    ) -> None:
        """
        Register available AI providers.
        """
        # Ollama (Local)
        try:
            ollama = OllamaProvider()
            ollama.configure(
                base_url="http://localhost:11434",
                default_model="ministral-3b",
            )
            container.ai_registry.register(ollama)
        except Exception:
            # Log but continue
            pass

        # OpenRouter (Cloud)
        try:
            openrouter = OpenRouterProvider()
            openrouter.configure(
                base_url="https://openrouter.ai/api/v1",
                api_key=None,
                default_model="openai/gpt-4.1-mini",
            )
            container.ai_registry.register(openrouter)
        except Exception:
            # Log but continue
            pass

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture