"""
===============================================================================
Agent Executor Loop
===============================================================================

Dependencies:
    - hermes.ai.conversation
    - hermes.ai.pipeline
    - hermes.ai.request
    - hermes.ai.response
    - hermes.ai.tool
    - hermes.agent.executor.builder
    - hermes.agent.executor.context_factory
    - hermes.agent.executor.conversation_manager
    - hermes.agent.executor.state
    - hermes.agent.executor.tool_runner
    - hermes.agent.planner.decision
    - hermes.agent.planner.hasher
    - hermes.agent.planner.planner
    - hermes.agent.planner.reasoning_planner
    - hermes.workspace.context

Consumes:
    - AIPipeline
    - ToolManager
    - AIConversation
    - AgentContextFactory
    - Planner
    - ExecutionContext

Produces:
    - AIResponse (Final)

Public API:
    - AgentExecutor.run()
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from hermes.ai.conversation import AIConversation
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ResponseFactory
from hermes.ai.tool import ToolManager, ToolResult, ToolStatus
from hermes.agent.executor.builder import RequestBuilder
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.conversation_manager import ConversationManager
from hermes.agent.executor.state import ExecutionState, ExecutionStatus, ToolFailureRecord
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.planner.decision import Decision
from hermes.agent.planner.hasher import ToolCallHasher
from hermes.agent.planner.planner import DefaultPlanner, Planner
from hermes.agent.planner.reasoning_planner import ReasoningPlanner
# FIX: Import from the new workspace package to avoid runtime collision
from hermes.workspace.context import ExecutionContext


class AgentExecutor:
    def __init__(
        self,
        pipeline: AIPipeline,
        tool_manager: ToolManager,
        provider: str,
        model: str = "",
        max_iterations: int = 10,
        use_cache: bool = False,
        context_factory: AgentContextFactory | None = None,
        planner: Planner | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._max_iterations = max_iterations
        self._use_cache = use_cache
        self._context_factory = context_factory or AgentContextFactory()
        
        if planner is None:
            self._planner = ReasoningPlanner(registry=self._tool_manager.registry)
        else:
            self._planner = planner

    def run(
        self,
        prompt: str,
        conversation: AIConversation,
        system_prompt: str | None = None,
        execution_context: ExecutionContext | None = None
    ) -> AIResponse:
        """
        Run the agent loop for a given prompt.
        Optionally accepts an ExecutionContext to bind this run to a Workspace.
        """
        exec_ctx = execution_context or ExecutionContext.create(workspace_id="ephemeral")
        
        state = ExecutionState(
            conversation=conversation,
            execution_id=exec_ctx.execution_id,
            metadata={"workspace_id": exec_ctx.workspace_id, **exec_ctx.metadata}
        )
        
        conv_manager = ConversationManager(conversation)
        tool_runner = ToolRunner(self._tool_manager)

        if system_prompt:
            conv_manager.append_system(system_prompt)

        conv_manager.append_user(prompt)
        
        state.status = ExecutionStatus.RUNNING
        state.updated_at = time.time()

        transient_messages: Optional[List[Dict[str, Any]]] = None

        for _ in range(self._max_iterations):
            state.iteration += 1
            state.updated_at = time.time()
            self._before_llm()

            message_dicts = RequestBuilder.build(conversation, transient_messages=transient_messages)
            transient_messages = None

            request = AIRequest(
                prompt="",
                input=None,
                provider=self._provider,
                model=self._model,
                task="chat",
                options={"messages": message_dicts},
                metadata={"execution_id": exec_ctx.execution_id},
            )

            response = self._pipeline.execute(
                provider=self._provider,
                request=request,
                context=None,
                use_cache=self._use_cache,
            )
            
            state.current_response = response
            state.response_history.append(response)

            self._after_llm(response)

            decision = self._planner.decide(response, state)

            if decision.decision == Decision.FINISH:
                conv_manager.append_assistant(response.text() or "")
                state.status = ExecutionStatus.FINISHED
                state.updated_at = time.time()
                return response
                
            elif decision.decision == Decision.ABORT:
                state.status = ExecutionStatus.FAILED
                state.updated_at = time.time()
                return ResponseFactory.error(
                    message=f"Execution aborted: {decision.reason}",
                    provider=self._provider,
                    model=self._model
                )
                
            elif decision.decision == Decision.CALL_TOOLS:
                conv_manager.append_tool_calls(response)
                state.status = ExecutionStatus.WAITING_FOR_TOOLS
                state.updated_at = time.time()

                self._before_tools()

                tool_context = self._context_factory.build(conversation)
                results = tool_runner.execute(response.tool_calls, context=tool_context)
                state.tool_results.extend(results)

                for i, tc in enumerate(response.tool_calls):
                    result = results[i]
                    if result.status == ToolStatus.FAILED:
                        fingerprint = ToolCallHasher.fingerprint(tc)
                        state.failure_history.append(ToolFailureRecord(
                            fingerprint=fingerprint,
                            tool_name=tc.function.name if tc.function else "unknown",
                            error=result.error or "Unknown error",
                            iteration=state.iteration
                        ))

                self._after_tools(results)

                for i, tc in enumerate(response.tool_calls):
                    result = results[i]
                    conv_manager.append_tool_result(tc, result)
                
                state.status = ExecutionStatus.RUNNING
                state.updated_at = time.time()
                continue
            
            elif decision.decision == Decision.RETRY:
                state.retry_count += 1
                transient_messages = [
                    {"role": "assistant", "content": response.text() or ""},
                    {"role": "system", "content": decision.feedback or "Please try again or use a tool."}
                ]
                state.status = ExecutionStatus.RUNNING
                state.updated_at = time.time()
                continue
            
            else:
                state.status = ExecutionStatus.FAILED
                state.updated_at = time.time()
                return ResponseFactory.error(
                    message=f"Planner returned unhandled decision: {decision.decision}",
                    provider=self._provider,
                    model=self._model,
                )

        state.status = ExecutionStatus.MAX_ITERATIONS
        state.updated_at = time.time()
        return ResponseFactory.error(
            message=f"Agent reached maximum iterations ({self._max_iterations}) without a final response.",
            provider=self._provider,
            model=self._model,
        )

    def _before_llm(self) -> None:
        pass

    def _after_llm(self, response: AIResponse) -> None:
        pass

    def _before_tools(self) -> None:
        pass

    def _after_tools(self, results: list[ToolResult]) -> None:
        pass