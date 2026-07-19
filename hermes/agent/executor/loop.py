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

Consumes:
    - AIPipeline
    - ToolManager
    - AIConversation
    - AgentContextFactory

Produces:
    - AIResponse (Final)

Public API:
    - AgentExecutor.run()

Integration Notes:
The executor maintains an ExecutionState object internally. This centralizes
runtime variables (iteration, status, responses) making future features like
planners, schedulers, and tracing significantly easier to implement.
The state object is passive; the executor mutates it directly.

TODO (Future PRs):
    - Expose ExecutionState via lifecycle hooks.
    - Add cooperative cancellation support via state.
===============================================================================
"""
from __future__ import annotations
import time
from hermes.ai.conversation import AIConversation
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ResponseFactory
from hermes.ai.tool import ToolManager, ToolResult
from hermes.agent.executor.builder import RequestBuilder
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.conversation_manager import ConversationManager
from hermes.agent.executor.state import ExecutionState, ExecutionStatus
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.planner.decision import Decision
from hermes.agent.planner.planner import DefaultPlanner, Planner

class AgentExecutor:
    """
    Orchestrates the ReAct loop.
    """
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
        self._planner = planner or DefaultPlanner()

    def run(
        self,
        prompt: str,
        conversation: AIConversation,
        system_prompt: str | None = None,
    ) -> AIResponse:
        """
        Run the agent loop for a given prompt.
        """
        state = ExecutionState(conversation=conversation)
        conv_manager = ConversationManager(conversation)
        tool_runner = ToolRunner(self._tool_manager)

        if system_prompt:
            conv_manager.append_system(system_prompt)

        conv_manager.append_user(prompt)

        state.status = ExecutionStatus.RUNNING
        state.updated_at = time.time()

        # ============================================================================
        # IMPORTANT
        #
        # The assistant/tool message ordering follows the OpenAI tool-calling contract.
        #
        # assistant(tool_calls)
        # ↓
        # tool(tool_call_id=...)
        # ↓
        # assistant(final)
        #
        # Changing this ordering will break compatibility with OpenAI-compatible
        # providers and future multi-step reasoning.
        # ============================================================================

        for _ in range(self._max_iterations):
            state.iteration += 1
            state.updated_at = time.time()
            self._before_llm()

            # 1. Serialize conversation to OpenAI-compatible messages
            message_dicts = RequestBuilder.build(conversation)

            # 2. Build AIRequest
            request = AIRequest(
                prompt="",
                input=None,
                provider=self._provider,
                model=self._model,
                task="chat",
                options={"messages": message_dicts},
                metadata={},
            )

            # 3. Execute via pipeline
            response = self._pipeline.execute(
                provider=self._provider,
                request=request,
                context=None,
                use_cache=self._use_cache,
            )

            state.current_response = response
            state.response_history.append(response)

            self._after_llm(response)

            # 4. Ask the planner what to do next
            decision = self._planner.decide(response, state)

            # 5. Execute the decision
            if decision.decision == Decision.FINISH:
                conv_manager.append_assistant(response.text() or "")
                state.status = ExecutionStatus.FINISHED
                state.updated_at = time.time()
                return response

            elif decision.decision == Decision.ABORT:
                state.status = ExecutionStatus.FAILED
                state.updated_at = time.time()
                return response

            elif decision.decision == Decision.CALL_TOOLS:
                # Append assistant tool call message to history
                conv_manager.append_tool_calls(response)
                state.status = ExecutionStatus.WAITING_FOR_TOOLS
                state.updated_at = time.time()

                self._before_tools()

                # Build context and execute tools
                tool_context = self._context_factory.build(conversation)
                results = tool_runner.execute(response.tool_calls, context=tool_context)
                state.tool_results.extend(results)

                self._after_tools(results)

                # Append tool results to conversation
                for i, tc in enumerate(response.tool_calls):
                    result = results[i]
                    conv_manager.append_tool_result(tc, result)

                state.status = ExecutionStatus.RUNNING
                state.updated_at = time.time()
                continue

            else:
                # Unhandled decision (e.g., RETRY, CONTINUE) - abort for now
                state.status = ExecutionStatus.FAILED
                state.updated_at = time.time()
                return ResponseFactory.error(
                    message=f"Planner returned unhandled decision: {decision.decision}",
                    provider=self._provider,
                    model=self._model,
                )

        # Loop exhausted
        state.status = ExecutionStatus.MAX_ITERATIONS
        state.updated_at = time.time()
        return ResponseFactory.error(
            message=f"Agent reached maximum iterations ({self._max_iterations}) without a final response.",
            provider=self._provider,
            model=self._model,
        )

    # ------------------------------------------------------------------
    # Lifecycle Hooks (for future extensibility)
    # ------------------------------------------------------------------

    def _before_llm(self) -> None:
        """Called before LLM execution."""
        pass

    def _after_llm(self, response: AIResponse) -> None:
        """Called after LLM execution."""
        pass

    def _before_tools(self) -> None:
        """Called before tool batch execution."""
        pass

    def _after_tools(self, results: list[ToolResult]) -> None:
        """Called after tool batch execution."""
        pass