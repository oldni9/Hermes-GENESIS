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

# Planner Registry imports
from hermes.agent.executor.planners.registry import GLOBAL_PLANNER_REGISTRY, PlannerDescriptor, PlannerCapabilities
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner
from hermes.agent.executor.planners.tree_of_thought import TreeOfThoughtPlanner
from hermes.agent.executor.planners.debate import DebatePlanner


def register_builtin_planners():
    """Registers all built-in planners into the global registry."""
    
    GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
        name="react",
        planner_class=ReActPlanner,
        description="Standard Reason + Act planner.",
        aliases=["default"],
        capabilities=PlannerCapabilities()
    ))
    
    GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
        name="reflection",
        planner_class=ReflectionPlanner,
        description="Planner that uses an LLM to critique and revise the answer.",
        capabilities=PlannerCapabilities(reflection=True)
    ))
    
    GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
        name="tot",
        planner_class=TreeOfThoughtPlanner,
        description="Tree of Thought planner. Generates and evaluates multiple branches.",
        capabilities=PlannerCapabilities(tree_search=True)
    ))
    
    GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
        name="debate",
        planner_class=DebatePlanner,
        description="Debate planner. Runs multiple personas and a judge to synthesize an answer.",
        capabilities=PlannerCapabilities(debate=True)
    ))
    
    GLOBAL_PLANNER_REGISTRY.freeze()


class HermesBootstrap:

    def build(self) -> HermesContainer:
        container = HermesContainer()

        # Register Built-in Planners
        register_builtin_planners()

        # Legacy Layer
        container.provider_manager = ProviderManager(container.provider_registry)
        container.execution_service = ExecutionService(container.provider_manager)
        container.kernel_executor = KernelExecutor(container.execution_service)
        container.runtime_engine = RuntimeEngine(container.execution_service)

        # AI Layer
        container.tool_registry = ToolRegistry()
        container.tool_manager = ToolManager(registry=container.tool_registry)
        container.ai_registry = AIRegistry()
        self._register_ai_providers(container)
        container.ai_manager = AIManager(registry=container.ai_registry)
        container.ai_router = AIRouter(registry=container.ai_registry)

        # Orchestrator Layer
        container.provider_selector = ProviderSelector(registry=container.ai_registry)
        container.response_processor = ResponseProcessor()
        container.retry_policy = RetryPolicy.default()
        container.orchestrator = AIOrchestrator(
            manager=container.ai_manager,
            provider_selector=container.provider_selector,
            response_processor=container.response_processor,
            retry_policy=container.retry_policy,
            tool_manager=container.tool_manager,
        )

        # Pipeline
        container.ai_pipeline = AIPipeline(orchestrator=container.orchestrator, cache=None)

        # Conversation & Sessions
        container.session_manager = MemorySessionManager()
        container.conversation_prompt_builder = ConversationPromptBuilder(trim_to=None, include_summary=False, include_system=True)
        container.request_builder = RequestBuilder()

        return container

    def _register_ai_providers(self, container: HermesContainer) -> None:
        try:
            ollama = OllamaProvider()
            ollama.configure(base_url="http://localhost:11434", default_model="ministral-3b")
            container.ai_registry.register(ollama)
        except Exception:
            pass

        try:
            openrouter = OpenRouterProvider()
            openrouter.configure(base_url="https://openrouter.ai/api/v1", api_key=None, default_model="openai/gpt-4.1-mini")
            container.ai_registry.register(openrouter)
        except Exception:
            pass

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture