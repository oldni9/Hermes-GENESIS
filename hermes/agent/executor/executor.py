"""
===============================================================================
Agent Executor (Facade)
===============================================================================

Sprint 13 Update:
Executor queries the UnifiedMemoryManager (using manager's default policy) and 
passes structured RetrievedContext to PlannerState.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Optional, Union

from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolManager
from hermes.core.runtime import RuntimePolicy, RuntimeContext, RuntimeMetrics, CancellationToken
from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.retrieval import RetrievedContext
from hermes.workspace.workspace import Workspace
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.planners.registry import GLOBAL_PLANNER_FACTORY
from hermes.agent.executor.trace import AgentTrace


class AgentExecutor:
    """Public facade for the Agent system."""

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_manager: ToolManager,
        provider: str,
        model: str = "",
        planner: Optional[Union[str, Planner]] = None,
        config: Optional[PlannerConfig] = None,
        memory_manager: Optional[UnifiedMemoryManager] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._config = config or PlannerConfig()
        self._memory_manager = memory_manager
        
        if isinstance(planner, Planner):
            self._planner = planner
        elif isinstance(planner, str):
            self._planner = GLOBAL_PLANNER_FACTORY.create(planner)
        elif self._config.planner_name:
            self._planner = GLOBAL_PLANNER_FACTORY.create(self._config.planner_name)
        else:
            from hermes.agent.executor.planners.react import ReActPlanner
            self._planner = ReActPlanner()

    def run(
        self,
        prompt: str,
        conversation: AIConversation,
        system_prompt: Optional[str] = None,
        workspace: Optional[Workspace] = None,
        policy: Optional[RuntimePolicy] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> AgentResult:
        """Run the agent loop for a given prompt."""
        conv_state = ConversationState(conversation)
        context_factory = AgentContextFactory()
        tool_runner = ToolRunner(self._tool_manager)
        request_builder = RequestBuilder(provider=self._provider, model=self._model)
        trace = AgentTrace()
        
        policy = policy or RuntimePolicy()
        cancellation_token = cancellation_token or CancellationToken()
        metrics = RuntimeMetrics()
        metrics.start()
        runtime_context = RuntimeContext(
            policy=policy,
            metrics=metrics,
            cancellation_token=cancellation_token
        )

        engine = ExecutionEngine(
            pipeline=self._pipeline,
            tool_runner=tool_runner,
            conv_state=conv_state,
            context_factory=context_factory,
            request_builder=request_builder,
            workspace=workspace,
            runtime_context=runtime_context,
        )

        # Sprint 13: Memory Retrieval (Manager owns default policy)
        retrieved_context: Optional[RetrievedContext] = None
        if self._memory_manager:
            retrieved_context = self._memory_manager.recall(prompt)

        # Prepare conversation (System prompt is kept pure)
        if system_prompt:
            conv_state.append_system_if_empty(system_prompt)
        conv_state.append_user(prompt)

        state = PlannerState(
            conversation=conv_state.conversation,
            trace=trace,
            iteration=0,
            reflection_count=0,
            runtime_context=runtime_context,
            objective=prompt,
            retrieved_context=retrieved_context
        )

        # Delegate to Planner
        result = self._planner.run(engine, state, self._config)
        
        metrics.finish()
        return result

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture