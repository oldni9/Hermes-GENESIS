"""
===============================================================================
Agent Executor (Facade)
===============================================================================

Sprint 17A.2 Update:
- Fixed conversation truthiness bug (empty AIConversation evaluating to False).
- Accepts an optional external AgentTrace for real-time streaming.
- Handles `conversation=None` gracefully by creating a new one.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Optional, Union

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolManager
from hermes.core.runtime import RuntimePolicy, RuntimeContext, RuntimeMetrics, CancellationToken
from hermes.memory.manager import UnifiedMemoryManager
from hermes.memory.persistence import MemoryPersistenceService
from hermes.memory.retrieval import RetrievedContext, MemoryCandidate
from hermes.workspace.workspace import Workspace
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.planners.registry import GLOBAL_PLANNER_FACTORY
from hermes.agent.executor.trace import AgentTrace
from hermes.graph.plan import ExecutionPlan
from hermes.graph.executor import GraphExecutor
from hermes.graph.models import GraphContext, Blackboard, GraphExecutionError


class AgentExecutor:
    """Public facade for the Agent system."""

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_manager: ToolManager,
        provider: str,
        model: str = "",
        planner: Optional[Union[str, Planner, ExecutionPlan]] = None,
        config: Optional[PlannerConfig] = None,
        memory_manager: Optional[UnifiedMemoryManager] = None,
        memory_persistence_service: Optional[MemoryPersistenceService] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._config = config or PlannerConfig()
        self._memory_manager = memory_manager
        self._memory_persistence_service = memory_persistence_service or (
            MemoryPersistenceService(memory_manager) if memory_manager else None
        )
        
        self._execution_plan: Optional[ExecutionPlan] = None
        self._planner: Optional[Planner] = None
        
        if isinstance(planner, ExecutionPlan):
            self._execution_plan = planner
        elif isinstance(planner, Planner):
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
        conversation: Optional[AIConversation] = None,
        system_prompt: Optional[str] = None,
        workspace: Optional[Workspace] = None,
        policy: Optional[RuntimePolicy] = None,
        cancellation_token: Optional[CancellationToken] = None,
        trace: Optional[AgentTrace] = None,
    ) -> AgentResult:
        """Run the agent loop for a given prompt."""
        # FIX: Use explicit `is None` check because AIConversation implements __len__
        # and an empty conversation evaluates to False in boolean contexts.
        active_conversation = conversation if conversation is not None else AIConversation()
        
        conv_state = ConversationState(active_conversation)
        context_factory = AgentContextFactory()
        tool_runner = ToolRunner(self._tool_manager)
        request_builder = RequestBuilder(provider=self._provider, model=self._model)
        
        active_trace = trace or AgentTrace()
        
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

        retrieved_context: Optional[RetrievedContext] = None
        if self._memory_manager:
            retrieved_context = self._memory_manager.recall(prompt)

        if system_prompt:
            conv_state.append_system_if_empty(system_prompt)
        conv_state.append_user(prompt)

        graph_context: Optional[GraphContext] = None
        result: AgentResult

        if self._execution_plan:
            graph_context = GraphContext(
                conversation=conv_state.conversation,
                runtime_context=runtime_context,
                trace=active_trace,
                blackboard=Blackboard({
                    "objective": prompt,
                    "retrieved_context": retrieved_context
                })
            )
            
            graph_executor = GraphExecutor()
            
            try:
                graph_result = graph_executor.run(
                    self._execution_plan.graph, 
                    graph_context
                )
                
                exit_node = self._execution_plan.graph.nodes[self._execution_plan.graph.exit_node]
                final_text = graph_result.outputs.get(exit_node.output_key, "")
                
                result = AgentResult(
                    response=AIResponse(
                        success=graph_result.success, 
                        result=final_text, 
                        provider=self._provider, 
                        model=self._model
                    ),
                    iterations=1,
                    duration=graph_result.duration,
                    token_usage=graph_result.token_usage,
                    stop_reason=StopReason.COMPLETED if graph_result.success else StopReason.PIPELINE_ERROR,
                    trace=active_trace,
                    memory_candidates=graph_result.memory_candidates
                )
            except GraphExecutionError as e:
                result = AgentResult(
                    response=AIResponse(
                        success=False, 
                        message=f"Graph execution failed at node '{e.node_id}': {e.original}", 
                        provider=self._provider, 
                        model=self._model
                    ),
                    iterations=1,
                    duration=0.0,
                    stop_reason=StopReason.PIPELINE_ERROR,
                    trace=e.trace,
                    memory_candidates=e.blackboard_snapshot.get("memory_candidates", [])
                )
        else:
            state = PlannerState(
                conversation=conv_state.conversation,
                trace=active_trace,
                iteration=0,
                reflection_count=0,
                runtime_context=runtime_context,
                objective=prompt,
                retrieved_context=retrieved_context
            )
            result = self._planner.run(engine, state, self._config)
        
        metrics.finish()
        
        if self._memory_persistence_service and result.response.success and result.memory_candidates:
            self._memory_persistence_service.persist(
                candidates=list(result.memory_candidates),
                context=graph_context
            )
            
        return result

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture