"""
===============================================================================
Agent ReAct Loop (Legacy)
===============================================================================

Dependencies:
    - time
    - typing
    - hermes.ai.conversation
    - hermes.ai.response
    - hermes.ai.tool
    - hermes.agent.executor.protocols
    - hermes.agent.executor.result
    - hermes.agent.executor.conversation_state
    - hermes.agent.executor.tool_runner
    - hermes.agent.executor.context_factory
    - hermes.agent.executor.request_builder
    - hermes.agent.executor.trace
    - hermes.agent.executor.serializer

Consumes:
    - PipelineProtocol
    - ToolRunner
    - ConversationState
    - AgentContextFactory
    - RequestBuilder
    - AgentTrace

Produces:
    - AgentResult

Public API:
    - ReActLoop
===============================================================================
"""

from __future__ import annotations

import time
from typing import Dict, Optional

from hermes.ai.response import AIResponse, ToolCall
from hermes.ai.tool import ToolResult
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.agent.executor.serializer import ToolResultSerializer
from hermes.workspace.workspace import Workspace


class ReActLoop:
    """
    The core ReAct (Reason + Act) orchestration engine.
    """

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_runner: ToolRunner,
        conv_state: ConversationState,
        context_factory: AgentContextFactory,
        request_builder: RequestBuilder,
        max_iterations: int,
        trace: AgentTrace,
        workspace: Optional[Workspace] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_runner = tool_runner
        self._conv_state = conv_state
        self._context_factory = context_factory
        self._request_builder = request_builder
        self._max_iterations = max_iterations
        self._trace = trace
        self._workspace = workspace

    def run(self) -> AgentResult:
        """Execute the ReAct loop."""
        start_time = time.time()

        for iteration in range(1, self._max_iterations + 1):
            self._trace.add_event(iteration, TraceEventType.ITERATION_START)

            # 1. Build request from conversation history
            self._trace.add_event(iteration, TraceEventType.LLM_START)
            request = self._request_builder.build(self._conv_state.conversation)

            # 2. Execute via pipeline
            response = self._pipeline.execute(
                provider=self._request_builder.provider,
                request=request,
                context=None,
                use_cache=False,
            )
            self._trace.add_event(
                iteration, 
                TraceEventType.LLM_FINISH, 
                {"success": response.success}
            )

            # Track token usage
            if response.usage:
                self._trace.add_token_usage(
                    response.usage.prompt_tokens, 
                    response.usage.completion_tokens
                )

            # 3. Check if pipeline failed
            if not response.success:
                self._trace.add_event(iteration, TraceEventType.FAILED)
                self._trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                self._trace.finalize()
                return AgentResult(
                    response=response,
                    iterations=iteration,
                    duration=time.time() - start_time,
                    token_usage={
                        "prompt_tokens": self._trace.metrics.total_prompt_tokens, 
                        "completion_tokens": self._trace.metrics.total_completion_tokens
                    },
                    stop_reason=StopReason.PIPELINE_ERROR,
                    trace=self._trace
                )

            # 4. Check if we are done (no tool calls)
            if not response.tool_calls:
                # Append final assistant message
                self._conv_state.append_assistant_text(response.text() or "")
                self._trace.add_event(
                    iteration, 
                    TraceEventType.COMPLETED, 
                    {"text_length": len(response.text() or "")}
                )
                self._trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                self._trace.finalize()
                return AgentResult(
                    response=response,
                    iterations=iteration,
                    duration=time.time() - start_time,
                    token_usage={
                        "prompt_tokens": self._trace.metrics.total_prompt_tokens, 
                        "completion_tokens": self._trace.metrics.total_completion_tokens
                    },
                    stop_reason=StopReason.COMPLETED,
                    trace=self._trace
                )

            # 5. We have tool calls. Append assistant tool call message to history
            self._conv_state.append_assistant_tool_calls(response)
            self._trace.add_event(
                iteration, 
                TraceEventType.TOOL_START, 
                {"tool_calls": len(response.tool_calls)}
            )

            # 6. Build context and execute tools
            tool_context = self._context_factory.build(
                conversation=self._conv_state.conversation,
                workspace=self._workspace
            )
            
            # ToolRunner returns a dict mapping call_id -> ToolResult
            results_map: Dict[str, ToolResult] = self._tool_runner.execute(response.tool_calls, tool_context)

            # 7. Serialize results and append to conversation
            tool_results_data = []
            for tc in response.tool_calls:
                result = results_map.get(tc.id)
                output_str = ToolResultSerializer.serialize(tc, result)
                tool_name = tc.function.name if tc.function else "unknown"
                
                self._conv_state.append_tool_message(
                    tool_call_id=tc.id,
                    tool_name=tool_name,
                    output=output_str
                )
                tool_results_data.append({
                    "call_id": tc.id, 
                    "tool_name": tool_name, 
                    "success": result.success if result else False
                })
            
            self._trace.add_event(
                iteration, 
                TraceEventType.TOOL_FINISH, 
                {"results": tool_results_data}
            )
            self._trace.add_event(iteration, TraceEventType.ITERATION_FINISH)

        # Loop exhausted
        final_response = AIResponse(
            success=False,
            message=f"Agent reached maximum iterations ({self._max_iterations}) without a final response.",
            provider=self._request_builder.provider,
            model=self._request_builder.model,
        )
        self._trace.add_event(self._max_iterations, TraceEventType.MAX_ITERATIONS_EXCEEDED)
        self._trace.add_event(self._max_iterations, TraceEventType.ITERATION_FINISH)
        self._trace.finalize()
        return AgentResult(
            response=final_response,
            iterations=self._max_iterations,
            duration=time.time() - start_time,
            token_usage={
                "prompt_tokens": self._trace.metrics.total_prompt_tokens, 
                "completion_tokens": self._trace.metrics.total_completion_tokens
            },
            stop_reason=StopReason.MAX_ITERATIONS,
            trace=self._trace
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture