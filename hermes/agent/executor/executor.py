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
from typing import Optional

from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolManager
from hermes.workspace.workspace import Workspace
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerConfig, PlannerState
from hermes.agent.executor.planners.react import ReActPlanner
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
        planner: Optional[Planner] = None,
        config: Optional[PlannerConfig] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._planner = planner or ReActPlanner()
        self._config = config or PlannerConfig()

    def run(
        self,
        prompt: str,
        conversation: AIConversation,
        system_prompt: Optional[str] = None,
        workspace: Optional[Workspace] = None,
    ) -> AgentResult:
        """Run the agent loop for a given prompt."""
        # 1. Initialize stateful components
        conv_state = ConversationState(conversation)
        context_factory = AgentContextFactory()
        tool_runner = ToolRunner(self._tool_manager)
        request_builder = RequestBuilder(provider=self._provider, model=self._model)
        trace = AgentTrace()

        # 2. Initialize the Execution Engine
        engine = ExecutionEngine(
            pipeline=self._pipeline,
            tool_runner=tool_runner,
            conv_state=conv_state,
            context_factory=context_factory,
            request_builder=request_builder,
            workspace=workspace,
        )

        # 3. Prepare conversation
        if system_prompt:
            conv_state.append_system_if_empty(system_prompt)
        conv_state.append_user(prompt)

        # 4. Initialize Planner State
        state = PlannerState(
            conversation=conv_state.conversation,
            trace=trace,
            iteration=0,
            reflection_count=0
        )

        # 5. Delegate to Planner
        return self._planner.run(engine, state, self._config)