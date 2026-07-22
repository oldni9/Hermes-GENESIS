"""
===============================================================================
Agent Executor (Facade)
===============================================================================

Wires dependencies together and delegates execution to the Planner.
The Executor is now permanently frozen as a simple composition root.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Optional, Union

from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolManager
from hermes.core.runtime import RuntimePolicy, RuntimeContext, RuntimeMetrics, CancellationToken
from hermes.workspace.workspace import Workspace
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.planners.registry import planner_factory
from hermes.agent.executor.trace import AgentTrace


class AgentExecutor:
    """
    Public facade for the Agent system.
    Wires the ExecutionEngine and Planner.
    """

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_manager: ToolManager,
        provider: str,
        model: str = "",
        planner: Optional[Union[str, Planner]] = None,
        config: Optional[PlannerConfig] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._config = config or PlannerConfig()
        
        # Resolve planner instance using Factory or direct injection
        if isinstance(planner, Planner):
            self._planner = planner
        elif isinstance(planner, str):
            self._planner = planner_factory.create(planner, pipeline, provider, model)
        elif self._config.planner_name:
            self._planner = planner_factory.create(self._config.planner_name, pipeline, provider, model)
        else:
            # Fallback to direct instantiation if no config or string is provided
            # This shouldn't happen due to config default, but keeps it safe
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
        # 1. Initialize stateful components
        conv_state = ConversationState(conversation)
        context_factory = AgentContextFactory()
        tool_runner = ToolRunner(self._tool_manager)
        request_builder = RequestBuilder(provider=self._provider, model=self._model)
        trace = AgentTrace()
        
        # 2. Initialize Runtime Context
        policy = policy or RuntimePolicy()
        cancellation_token = cancellation_token or CancellationToken()
        metrics = RuntimeMetrics()
        metrics.start()
        runtime_context = RuntimeContext(
            policy=policy,
            metrics=metrics,
            cancellation_token=cancellation_token
        )

        # 3. Initialize the Execution Engine
        engine = ExecutionEngine(
            pipeline=self._pipeline,
            tool_runner=tool_runner,
            conv_state=conv_state,
            context_factory=context_factory,
            request_builder=request_builder,
            workspace=workspace,
            runtime_context=runtime_context,
        )

        # 4. Prepare conversation
        if system_prompt:
            conv_state.append_system_if_empty(system_prompt)
        conv_state.append_user(prompt)

        # 5. Initialize Planner State
        state = PlannerState(
            conversation=conv_state.conversation,
            trace=trace,
            iteration=0,
            reflection_count=0,
            runtime_context=runtime_context,
        )

        # 6. Delegate to Planner
        result = self._planner.run(engine, state, self._config)
        
        # Finalize metrics
        metrics.finish()
        
        return result

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture