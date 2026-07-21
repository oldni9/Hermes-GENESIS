import pytest
import time
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.agent.executor import AgentExecutor, AgentResult, AgentTrace, TraceEventType, PlannerConfig
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.planners.base import Planner
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import PlannerState
from hermes.ai.tool import ToolManager, ToolRegistry


@pytest.fixture
def mock_pipeline():
    return MagicMock(spec=PipelineProtocol)

@pytest.fixture
def tool_manager():
    tm = ToolManager(ToolRegistry())
    def echo_tool(text: str) -> str:
        return f"Echo: {text}"
    tm.register_function(name="echo", func=echo_tool, description="Echoes text")
    return tm

@pytest.fixture
def conversation():
    return AIConversation(title="Test Agent Loop")

def make_text_response(text: str) -> AIResponse:
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=text),
        finish_reason="stop"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], result=text)

def make_tool_response(call_id: str, func_name: str, args: dict = None) -> AIResponse:
    tc = ToolCall(id=call_id, type="function", function=FunctionCall(name=func_name, arguments=args or {}))
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=""),
        finish_reason="tool_calls"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], tool_calls=[tc])

def test_agent_no_tools_completes_immediately(mock_pipeline, tool_manager, conversation):
    mock_pipeline.execute.return_value = make_text_response("Hello!")
    agent = AgentExecutor(mock_pipeline, tool_manager, "test", "test-model")
    result = agent.run("Hi", conversation)
    
    assert result.response.success
    assert result.response.text() == "Hello!"
    assert result.iterations == 1
    assert result.stop_reason == "completed"

def test_agent_executes_tool_and_loops(mock_pipeline, tool_manager, conversation):
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "echo", {"text": "Hello Tool"}),
        make_text_response("I have echoed the text.")
    ]
    agent = AgentExecutor(mock_pipeline, tool_manager, "test", "test-model")
    result = agent.run("Echo 'Hello Tool'", conversation)
    
    assert result.response.success
    assert result.response.text() == "I have echoed the text."
    
    msgs = conversation.messages()
    assert len(msgs) == 4
    assert msgs[2].role.value == "tool"
    assert msgs[2].content == "Echo: Hello Tool"

def test_agent_max_iterations(mock_pipeline, tool_manager, conversation):
    # A custom planner that always forces another iteration, ignoring the engine's success
    class LoopPlanner(Planner):
        def run(self, engine: ExecutionEngine, state: PlannerState, config: PlannerConfig) -> AgentResult:
            start_time = time.time()
            for iteration in range(1, config.max_iterations + 1):
                state.iteration = iteration
                state.trace.add_event(iteration, TraceEventType.ITERATION_START)
                state.trace.add_event(iteration, TraceEventType.PLANNER_ITERATION)
                
                # Execute turn but ignore the result to force a loop
                engine.execute_turn(state.trace, iteration, config)
                
                state.trace.add_event(iteration, TraceEventType.PLANNER_DECISION, {"action": "continue"})
                state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                
            final_response = AIResponse(
                success=False,
                message=f"Agent reached maximum iterations ({config.max_iterations}) without a final response.",
                provider="test",
                model="test-model"
            )
            state.trace.add_event(config.max_iterations, TraceEventType.MAX_ITERATIONS_EXCEEDED)
            state.trace.finalize()
            return AgentResult(
                response=final_response,
                iterations=config.max_iterations,
                duration=time.time() - start_time,
                token_usage={"prompt_tokens": 0, "completion_tokens": 0},
                stop_reason="max_iterations",
                trace=state.trace
            )

    mock_pipeline.execute.return_value = make_text_response("loop")
    agent = AgentExecutor(
        mock_pipeline, 
        tool_manager, 
        "test", 
        "test-model", 
        planner=LoopPlanner(), 
        config=PlannerConfig(max_iterations=3)
    )
    result = agent.run("Keep looping", conversation)
    
    assert not result.response.success
    assert result.stop_reason == "max_iterations"
    assert result.iterations == 3
    # 3 engine calls
    assert mock_pipeline.execute.call_count == 3