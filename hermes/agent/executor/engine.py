"""
===============================================================================
Execution Engine
===============================================================================

Handles the mechanics of running LLM calls and tool execution.
It loops internally until the LLM stops requesting tools.
It is completely stateless and instructed by the Planner.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Dict

from hermes.ai.response import AIResponse, ToolCall
from hermes.ai.tool import ToolResult
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.agent.executor.serializer import ToolResultSerializer
from hermes.workspace.workspace import Workspace


class ExecutionEngine:
    """
    Executes a single turn of reasoning + acting.
    Returns the final LLM response for that turn.
    """

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_runner: ToolRunner,
        conv_state: ConversationState,
        context_factory: AgentContextFactory,
        request_builder: RequestBuilder,
        workspace: Workspace | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_runner = tool_runner
        self._conv_state = conv_state
        self._context_factory = context_factory
        self._request_builder = request_builder
        self._workspace = workspace

    def execute_turn(self, trace: AgentTrace, iteration: int, config) -> AIResponse:
        """Run the LLM -> Tool loop until a final answer is reached or tools max out."""
        trace.add_event(iteration, TraceEventType.EXECUTION_START)
        
        for tool_iter in range(1, config.engine_max_iterations + 1):
            trace.add_event(iteration, TraceEventType.LLM_START)
            request = self._request_builder.build(self._conv_state.conversation)
            
            response = self._pipeline.execute(
                provider=self._request_builder.provider,
                request=request,
                context=None,
                use_cache=False,
            )
            trace.add_event(iteration, TraceEventType.LLM_FINISH, {"success": response.success})

            if response.usage:
                trace.add_token_usage(
                    response.usage.prompt_tokens, 
                    response.usage.completion_tokens
                )

            if not response.success:
                trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": False})
                return response

            if not response.tool_calls:
                trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": True})
                return response

            # Handle Tool Calls
            self._conv_state.append_assistant_tool_calls(response)
            trace.add_event(iteration, TraceEventType.TOOL_START, {"tool_calls": len(response.tool_calls)})

            tool_context = self._context_factory.build(
                conversation=self._conv_state.conversation,
                workspace=self._workspace
            )
            
            results_map: Dict[str, ToolResult] = self._tool_runner.execute(response.tool_calls, tool_context)

            for tc in response.tool_calls:
                result = results_map.get(tc.id)
                output_str = ToolResultSerializer.serialize(tc, result)
                tool_name = tc.function.name if tc.function else "unknown"
                self._conv_state.append_tool_message(
                    tool_call_id=tc.id,
                    tool_name=tool_name,
                    output=output_str
                )
            
            trace.add_event(iteration, TraceEventType.TOOL_FINISH)

        # Exceeded max tool iterations
        trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": False, "reason": "engine_max_iterations"})
        return AIResponse(
            success=False,
            message=f"Execution engine exceeded max iterations ({config.engine_max_iterations}).",
            provider=self._request_builder.provider,
            model=self._request_builder.model,
        )