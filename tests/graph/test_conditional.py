"""
===============================================================================
Tests for Router Node (Sprint 15.1)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import PlannerConfig
from hermes.agent.executor.trace import AgentTrace
from hermes.core.runtime import RuntimeContext
from hermes.runtime.parallel import ParallelExecutionService
from hermes.graph.models import ExecutionGraph, ExecutionEdge, GraphContext, Blackboard, NodeResult
from hermes.graph.nodes.base import LLMNode
from hermes.graph.nodes.conditional import RouterNode
from hermes.graph.nodes.parallel import ParallelNode, TextConcatStrategy
from hermes.graph.executor import GraphExecutor


def make_response(text: str):
    return AIResponse(success=True, result=text, provider="test", model="test-model")


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock(spec=ExecutionEngine)
    engine.provider = "test"
    engine.model = "test-model"
    return engine

@pytest.fixture
def graph_context() -> GraphContext:
    return GraphContext(
        conversation=AIConversation(),
        runtime_context=RuntimeContext(),
        trace=AgentTrace(),
        blackboard=Blackboard({"objective": "Test objective", "score": 85})
    )

@pytest.fixture
def graph_executor() -> GraphExecutor:
    return GraphExecutor()

def test_router_node_selects_correct_route(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor):
    """RouterNode should execute the subgraph matching the predicate."""
    mock_engine.execute_ephemeral.return_value = make_response("Excellent result")
    
    graph_excellent = ExecutionGraph(
        nodes={"ex": LLMNode("ex", "Excellent", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="ex",
        exit_node="ex"
    )
    graph_good = ExecutionGraph(
        nodes={"gd": LLMNode("gd", "Good", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="gd",
        exit_node="gd"
    )
    
    def predicate(bb: dict) -> str:
        if bb.get("score") > 90: return "excellent"
        if bb.get("score") > 80: return "good"
        return "fail"
    
    router = RouterNode(
        node_id="router1",
        routes={"excellent": graph_excellent, "good": graph_good},
        predicate=predicate,
        graph_runner=graph_executor,
        default_route="good"
    )
    result = router.execute(graph_context)
    
    # Since score is 85, it should select "good", which returns "Excellent result" due to mock
    assert result.success
    assert result.outputs["text"] == "Excellent result"
    assert result.metadata.trace is not None

def test_router_node_uses_default_route(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor):
    """RouterNode should use default route if predicate returns None or missing key."""
    mock_engine.execute_ephemeral.return_value = make_response("Default result")
    
    graph_default = ExecutionGraph(
        nodes={"def": LLMNode("def", "Default", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="def",
        exit_node="def"
    )
    
    def predicate(bb: dict) -> str:
        return "missing_route" # Not in routes dict
        
    router = RouterNode(
        node_id="router2",
        routes={"default": graph_default},
        predicate=predicate,
        graph_runner=graph_executor,
        default_route="default"
    )
    result = router.execute(graph_context)
    
    assert result.success
    assert result.outputs["text"] == "Default result"

def test_router_node_fails_if_no_match_and_no_default(graph_context: GraphContext, graph_executor: GraphExecutor):
    """RouterNode should fail if no route matches and no default is provided."""
    def predicate(bb: dict) -> str:
        return "impossible"
        
    router = RouterNode(
        node_id="router3",
        routes={},
        predicate=predicate,
        graph_runner=graph_executor
    )
    result = router.execute(graph_context)
    
    assert not result.success
    assert result.stop is True
    assert "error" in result.outputs

def test_router_node_nested_router(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor):
    """RouterNode should support nested RouterNodes."""
    mock_engine.execute_ephemeral.return_value = make_response("Deep Result")
    
    graph_deep = ExecutionGraph(
        nodes={"deep": LLMNode("deep", "Deep", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="deep",
        exit_node="deep"
    )
    
    # Inner router
    inner_router = RouterNode(
        node_id="inner_router",
        routes={"deep": graph_deep},
        predicate=lambda bb: "deep",
        graph_runner=graph_executor,
        default_route="deep"
    )
    
    graph_inner = ExecutionGraph(
        nodes={"inner": inner_router},
        edges=[],
        entry_node="inner",
        exit_node="inner"
    )
    
    # Outer router
    outer_router = RouterNode(
        node_id="outer_router",
        routes={"inner": graph_inner},
        predicate=lambda bb: "inner",
        graph_runner=graph_executor,
        default_route="inner"
    )
    
    result = outer_router.execute(graph_context)
    
    assert result.success
    assert result.outputs["text"] == "Deep Result"

def test_router_node_parallel_inside(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor):
    """RouterNode should support ParallelNode inside its routes."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Parallel A"), 
        make_response("Parallel B")
    ]
    
    graph_a = ExecutionGraph(
        nodes={"a": LLMNode("a", "A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a",
        exit_node="a"
    )
    graph_b = ExecutionGraph(
        nodes={"b": LLMNode("b", "B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par_in_router",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=ParallelExecutionService(max_workers=2),
        graph_runner=graph_executor
    )
    
    graph_par = ExecutionGraph(
        nodes={"par": parallel_node},
        edges=[],
        entry_node="par",
        exit_node="par"
    )
    
    router = RouterNode(
        node_id="router_par",
        routes={"par": graph_par},
        predicate=lambda bb: "par",
        graph_runner=graph_executor,
        default_route="par"
    )
    
    result = router.execute(graph_context)
    
    assert result.success
    assert "Parallel A" in result.outputs["text"]
    assert "Parallel B" in result.outputs["text"]

def test_router_node_3_level_nesting(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor):
    """Verify 3-level nesting: Router -> Parallel -> Router -> Graph"""
    mock_engine.execute_ephemeral.return_value = make_response("Deep Success")
    
    graph_deep = ExecutionGraph(
        nodes={"d": LLMNode("d", "D", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="d",
        exit_node="d"
    )
    
    router_inner = RouterNode(
        node_id="ri",
        routes={"d": graph_deep},
        predicate=lambda bb: "d",
        graph_runner=graph_executor
    )
    
    graph_inner_router = ExecutionGraph(
        nodes={"ri": router_inner},
        edges=[],
        entry_node="ri",
        exit_node="ri"
    )
    
    parallel_node = ParallelNode(
        node_id="pi",
        branches=[graph_inner_router],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=ParallelExecutionService(max_workers=1),
        graph_runner=graph_executor
    )
    
    graph_par = ExecutionGraph(
        nodes={"pi": parallel_node},
        edges=[],
        entry_node="pi",
        exit_node="pi"
    )
    
    router_outer = RouterNode(
        node_id="ro",
        routes={"pi": graph_par},
        predicate=lambda bb: "pi",
        graph_runner=graph_executor
    )
    
    result = router_outer.execute(graph_context)
    
    assert result.success
    assert "Deep Success" in result.outputs["text"]