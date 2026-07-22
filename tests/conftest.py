"""
===============================================================================
Shared Test Fixtures & Helpers
===============================================================================
"""
import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseChoice, ResponseMessage, ResponseUsage
from hermes.ai.tool import ToolManager, ToolRegistry
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.trace import AgentTrace
from hermes.core.runtime import RuntimeContext


def make_text_response(text: str, tokens: int = 10) -> AIResponse:
    """Helper to create a standard text response with token usage."""
    prompt_t = tokens // 2
    comp_t = tokens - prompt_t  # Ensures total is exactly `tokens` for odd numbers
    
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=text),
        finish_reason="stop"
    )
    usage = ResponseUsage(
        prompt_tokens=prompt_t,
        completion_tokens=comp_t,
        total_tokens=tokens
    )
    return AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[choice],
        result=text,
        usage=usage
    )


@pytest.fixture
def mock_pipeline() -> MagicMock:
    return MagicMock(spec=PipelineProtocol)


@pytest.fixture
def tool_manager() -> ToolManager:
    return ToolManager(ToolRegistry())


@pytest.fixture
def execution_engine(mock_pipeline, tool_manager):
    """Provides a fully wired ExecutionEngine for direct unit testing."""
    conv_state = ConversationState(AIConversation())
    context_factory = AgentContextFactory()
    request_builder = RequestBuilder(provider="test", model="test-model")
    trace = AgentTrace()
    runtime_context = RuntimeContext()
    
    engine = ExecutionEngine(
        pipeline=mock_pipeline,
        tool_runner=ToolRunner(tool_manager),
        conv_state=conv_state,
        context_factory=context_factory,
        request_builder=request_builder,
        workspace=None,
        runtime_context=runtime_context
    )
    
    return engine, trace, runtime_context


@pytest.fixture(autouse=True)
def ensure_planners_registered():
    """Ensures the global planner registry has builtin planners for tests."""
    from hermes.agent.executor.planners.registry import GLOBAL_PLANNER_REGISTRY, PlannerDescriptor
    from hermes.agent.executor.planners.react import ReActPlanner
    from hermes.agent.executor.planners.reflection import ReflectionPlanner
    from hermes.agent.executor.planners.tree_of_thought import TreeOfThoughtPlanner
    
    # Reset registry state if it was frozen by a previous test
    if GLOBAL_PLANNER_REGISTRY._frozen:
        GLOBAL_PLANNER_REGISTRY._frozen = False
        GLOBAL_PLANNER_REGISTRY.clear()
        
    if not GLOBAL_PLANNER_REGISTRY.contains("react"):
        GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
            name="react",
            planner_class=ReActPlanner,
            description="Standard Reason + Act planner.",
            aliases=["default"]
        ))
        GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
            name="reflection",
            planner_class=ReflectionPlanner,
            description="Planner that uses an LLM to critique and revise the answer."
        ))
        GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(
            name="tot",
            planner_class=TreeOfThoughtPlanner,
            description="Tree of Thought planner.",
            capabilities=GLOBAL_PLANNER_REGISTRY.get("react").capabilities.__class__(tree_search=True)
        ))