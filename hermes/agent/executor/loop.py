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
    - hermes.agent.executor.conversation_manager
    - hermes.agent.executor.tool_runner

Consumes:
    - AIPipeline
    - ToolManager
    - AIConversation

Produces:
    - AIResponse (Final)

Public API:
    - AgentExecutor.run()
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ResponseFactory
from hermes.ai.tool import ToolManager
from hermes.agent.executor.builder import RequestBuilder
from hermes.agent.executor.conversation_manager import ConversationManager
from hermes.agent.executor.tool_runner import ToolRunner


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
    ) -> None:
        self._pipeline = pipeline
        self._tool_manager = tool_manager
        self._provider = provider
        self._model = model
        self._max_iterations = max_iterations
        self._use_cache = use_cache

    def run(
        self,
        prompt: str,
        conversation: AIConversation,
        system_prompt: str | None = None,
    ) -> AIResponse:
        """
        Run the agent loop for a given prompt.
        """
        conv_manager = ConversationManager(conversation)
        tool_runner = ToolRunner(self._tool_manager)

        if system_prompt:
            conv_manager.append_system(system_prompt)

        conv_manager.append_user(prompt)

        # ============================================================================
        # IMPORTANT
        #
        # The assistant/tool message ordering follows the OpenAI tool-calling contract.
        #
        # assistant(tool_calls)
        #       ↓
        # tool(tool_call_id=...)
        #       ↓
        # assistant(final)
        #
        # Changing this ordering will break compatibility with OpenAI-compatible
        # providers and future multi-step reasoning.
        # ============================================================================

        for _ in range(self._max_iterations):
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

            self._after_llm(response)

            if not response.success:
                return response

            # 4. Check if we are done (no tool calls)
            if not response.tool_calls:
                conv_manager.append_assistant(response.text() or "")
                return response

            # 5. We have tool calls. Append assistant tool call message to history
            conv_manager.append_tool_calls(response)

            self._before_tools()

            # 6. Execute the tools
            results = tool_runner.execute(response.tool_calls)

            self._after_tools(results)

            # 7. Append tool results to conversation
            for i, tc in enumerate(response.tool_calls):
                result = results[i]
                conv_manager.append_tool_result(tc, result)

        # Loop exhausted
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

    def _after_tools(self, results: list) -> None:
        """Called after tool batch execution."""
        pass