"""
===============================================================================
Tests for Parallel Node (Sprint 15.1)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import PlannerConfig
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.core.runtime import RuntimeContext
from hermes.runtime.parallel import ParallelExecutionService
from hermes.graph.models import ExecutionGraph, ExecutionEdge, GraphContext, Blackboard, NodeResult
from hermes.graph.nodes.base import LLMNode
from hermes.graph.nodes.parallel import ParallelNode, ListMergeStrategy, TextConcatStrategy, ParallelExecutionPolicy
from hermes.graph.nodes.conditional import RouterNode
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
        blackboard=Blackboard({"objective": "Test objective"})
    )

@pytest.fixture
def graph_executor() -> GraphExecutor:
    return GraphExecutor()

@pytest.fixture
def parallel_runner() -> ParallelExecutionService:
    return ParallelExecutionService(max_workers=2)

def test_parallel_node_list_merge(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """ParallelNode should execute subgraphs concurrently and merge outputs into a list."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Branch A"), 
        make_response("Branch B")
    ]
    
    graph_a = ExecutionGraph(
        nodes={"a": LLMNode("a", "Prompt A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a",
        exit_node="a"
    )
    graph_b = ExecutionGraph(
        nodes={"b": LLMNode("b", "Prompt B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par1",
        branches=[graph_a, graph_b],
        merge_strategy=ListMergeStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor
    )
    
    result = parallel_node.execute(graph_context)
    
    assert result.success
    assert len(result.outputs["merged_outputs"]) == 2
    assert {"text": "Branch A"} in result.outputs["merged_outputs"]
    assert {"text": "Branch B"} in result.outputs["merged_outputs"]
    assert len(result.metadata.branch_metadata) == 2

def test_parallel_node_all_success_fails_on_error(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """ALL_SUCCESS policy should fail if any branch fails."""
    class CrashNode(LLMNode):
        def execute(self, context):
            return NodeResult(success=False, stop=True)
            
    mock_engine.execute_ephemeral.return_value = make_response("Success")
    
    graph_a = ExecutionGraph(
        nodes={"a": LLMNode("a", "A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a",
        exit_node="a"
    )
    graph_b = ExecutionGraph(
        nodes={"b": CrashNode("b", "B", mock_engine, PlannerConfig())},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par_fail",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor,
        policy=ParallelExecutionPolicy.ALL_SUCCESS
    )
    
    result = parallel_node.execute(graph_context)
    
    assert not result.success
    assert "1 branches failed" in result.outputs["error"]

def test_parallel_node_nested(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """ParallelNode should support nested ParallelNodes."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Nested A1"), 
        make_response("Nested A2"),
        make_response("Branch B")
    ]
    
    nested_a = ExecutionGraph(
        nodes={"a1": LLMNode("a1", "Prompt A1", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a1",
        exit_node="a1"
    )
    nested_a2 = ExecutionGraph(
        nodes={"a2": LLMNode("a2", "Prompt A2", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a2",
        exit_node="a2"
    )
    
    graph_a = ExecutionGraph(
        nodes={
            "par_a": ParallelNode(
                node_id="par_a",
                branches=[nested_a, nested_a2],
                merge_strategy=TextConcatStrategy(),
                parallel_runner=parallel_runner,
                graph_runner=graph_executor
            )
        },
        edges=[],
        entry_node="par_a",
        exit_node="par_a"
    )
    
    graph_b = ExecutionGraph(
        nodes={"b": LLMNode("b", "Prompt B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par_root",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor
    )
    
    result = parallel_node.execute(graph_context)
    
    assert result.success
    assert "Nested A1" in result.outputs["text"]
    assert "Nested A2" in result.outputs["text"]
    assert "Branch B" in result.outputs["text"]

def test_parallel_node_empty_branches(graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """Should fail if branches list is empty."""
    with pytest.raises(ValueError, match="at least one branch"):
        ParallelNode(
            node_id="par_empty",
            branches=[],
            merge_strategy=ListMergeStrategy(),
            parallel_runner=parallel_runner,
            graph_runner=graph_executor
        )

def test_parallel_node_best_effort(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """BEST_EFFORT policy should proceed if some branches fail."""
    class CrashNode(LLMNode):
        def execute(self, context):
            return NodeResult(success=False, stop=True)
            
    graph_a = ExecutionGraph(
        nodes={"a": LLMNode("a", "A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a",
        exit_node="a"
    )
    graph_b = ExecutionGraph(
        nodes={"b": CrashNode("b", "B", mock_engine, PlannerConfig())},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    mock_engine.execute_ephemeral.return_value = make_response("Success")
    
    parallel_node = ParallelNode(
        node_id="par3",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor,
        policy=ParallelExecutionPolicy.BEST_EFFORT
    )
    
    result = parallel_node.execute(graph_context)
    
    assert result.success
    assert "Success" in result.outputs["text"]

def test_parallel_trace_events_emitted(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """Verify PARALLEL_STARTED, BRANCH_STARTED, BRANCH_FINISHED, MERGE_STARTED, MERGE_FINISHED are emitted."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("A"), 
        make_response("B")
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
        node_id="par4",
        branches=[graph_a, graph_b],
        merge_strategy=ListMergeStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor
    )
    
    parallel_node.execute(graph_context)
    
    event_types = [e.event_type for e in graph_context.trace.events]
    
    assert TraceEventType.PARALLEL_STARTED in event_types
    assert TraceEventType.PARALLEL_BRANCH_STARTED in event_types
    assert TraceEventType.PARALLEL_BRANCH_FINISHED in event_types
    assert TraceEventType.MERGE_STARTED in event_types
    assert TraceEventType.MERGE_FINISHED in event_types

def test_parallel_node_router_inside(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """ParallelNode should support RouterNode inside its branches."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Router Branch A"), 
        make_response("Parallel Branch B")
    ]
    
    graph_router_a = ExecutionGraph(
        nodes={"ra": LLMNode("ra", "Router A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="ra",
        exit_node="ra"
    )
    graph_router_b = ExecutionGraph(
        nodes={"rb": LLMNode("rb", "Router B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="rb",
        exit_node="rb"
    )
    
    router_node = RouterNode(
        node_id="router_in_par",
        routes={"a": graph_router_a, "b": graph_router_b},
        predicate=lambda bb: "a",
        graph_runner=graph_executor,
        default_route="b"
    )
    
    graph_a = ExecutionGraph(
        nodes={"router": router_node},
        edges=[],
        entry_node="router",
        exit_node="router"
    )
    
    graph_b = ExecutionGraph(
        nodes={"b": LLMNode("b", "Parallel B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par_router",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor
    )
    
    result = parallel_node.execute(graph_context)
    
    assert result.success
    assert "Router Branch A" in result.outputs["text"]
    assert "Parallel Branch B" in result.outputs["text"]

def test_parallel_node_blackboard_isolation(mock_engine: MagicMock, graph_context: GraphContext, graph_executor: GraphExecutor, parallel_runner: ParallelExecutionService):
    """Branches should not overwrite each other's blackboard keys."""
    class BlackboardWriterNode(LLMNode):
        def execute(self, context: GraphContext) -> NodeResult:
            context.blackboard.update({"branch_data": self.id})
            return NodeResult(success=True, outputs={"text": self.id})
            
    graph_a = ExecutionGraph(
        nodes={"a": BlackboardWriterNode("a", "A", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="a",
        exit_node="a"
    )
    graph_b = ExecutionGraph(
        nodes={"b": BlackboardWriterNode("b", "B", mock_engine, PlannerConfig(), output_key="text")},
        edges=[],
        entry_node="b",
        exit_node="b"
    )
    
    parallel_node = ParallelNode(
        node_id="par_iso",
        branches=[graph_a, graph_b],
        merge_strategy=TextConcatStrategy(),
        parallel_runner=parallel_runner,
        graph_runner=graph_executor
    )
    
    result = parallel_node.execute(graph_context)
    
    assert result.success
    assert "branch_data" not in graph_context.blackboard.to_dict()