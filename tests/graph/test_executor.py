"""
===============================================================================
Tests for Graph Executor (Sprint 14)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseUsage
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import PlannerState, PlannerConfig
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.core.runtime import RuntimeContext
from hermes.graph.models import ExecutionGraph, ExecutionEdge, NodeResult, GraphContext, Blackboard, GraphExecutionError
from hermes.graph.nodes import LLMNode, PlannerNode, JudgeNode
from hermes.graph.executor import GraphExecutor
from hermes.graph.plan import ExecutionPlan


def make_response(text: str) -> AIResponse:
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

def test_single_node_graph(mock_engine: MagicMock, graph_context: GraphContext):
    """A graph with a single LLMNode should execute and return its text."""
    mock_engine.execute_ephemeral.return_value = make_response("Single node output")
    
    nodes = {"n1": LLMNode("n1", "Prompt: {objective}", mock_engine, PlannerConfig())}
    graph = ExecutionGraph(nodes=nodes, edges=[], entry_node="n1", exit_node="n1")
    
    executor = GraphExecutor()
    result = executor.run(graph, graph_context)
    
    assert result.success
    assert result.outputs["n1"] == "Single node output"

def test_multi_node_dag_blackboard_propagation(mock_engine: MagicMock, graph_context: GraphContext):
    """Data should flow from node A to node B via the blackboard using namespaced keys."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Intermediate"), # Node A
        make_response("Final")         # Node B
    ]
    
    nodes = {
        "a": LLMNode("a", "Generate step for {objective}", mock_engine, PlannerConfig()),
        "b": LLMNode("b", "Use this data: {a}", mock_engine, PlannerConfig())
    }
    edges = [ExecutionEdge(source="a", target="b")]
    graph = ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="b")
    
    executor = GraphExecutor()
    result = executor.run(graph, graph_context)
    
    assert result.outputs["b"] == "Final"
    
    second_call_args = mock_engine.execute_ephemeral.call_args_list[1][0][3]
    assert "Use this data: Intermediate" == second_call_args

def test_judge_node_fan_in(mock_engine: MagicMock, graph_context: GraphContext):
    """JudgeNode should synthesize inputs from multiple parents."""
    mock_engine.execute_ephemeral.side_effect = [
        make_response("Start"),     # Start Node
        make_response("Branch A"),  # Node A
        make_response("Branch B"),  # Node B
        make_response("Synthesized")# Judge Node
    ]
    
    nodes = {
        "start": LLMNode("start", "Start", mock_engine, PlannerConfig()),
        "a": LLMNode("a", "A", mock_engine, PlannerConfig()),
        "b": LLMNode("b", "B", mock_engine, PlannerConfig()),
        "judge": JudgeNode("judge", "Synthesize:\n{inputs}", ["a", "b"], mock_engine, PlannerConfig())
    }
    edges = [
        ExecutionEdge(source="start", target="a"),
        ExecutionEdge(source="start", target="b"),
        ExecutionEdge(source="a", target="judge"),
        ExecutionEdge(source="b", target="judge")
    ]
    graph = ExecutionGraph(nodes=nodes, edges=edges, entry_node="start", exit_node="judge")
    
    executor = GraphExecutor()
    result = executor.run(graph, graph_context)
    
    assert result.outputs["judge"] == "Synthesized"
    
    judge_call_args = mock_engine.execute_ephemeral.call_args_list[3][0][3]
    assert "Input 1:\nBranch A" in judge_call_args
    assert "Input 2:\nBranch B" in judge_call_args

def test_cycle_detection():
    """Graph initialization should raise if a cycle is detected."""
    # Graph: start -> a, a <-> b, a -> end. (Has 1 root, 1 leaf, but contains a cycle)
    nodes = {
        "start": LLMNode("start", "S", MagicMock(), PlannerConfig()),
        "a": LLMNode("a", "A", MagicMock(), PlannerConfig()),
        "b": LLMNode("b", "B", MagicMock(), PlannerConfig()),
        "end": LLMNode("end", "E", MagicMock(), PlannerConfig())
    }
    edges = [
        ExecutionEdge(source="start", target="a"),
        ExecutionEdge(source="a", target="b"),
        ExecutionEdge(source="b", target="a"), # Cycle here
        ExecutionEdge(source="a", target="end")
    ]
    with pytest.raises(ValueError, match="contains a cycle"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="start", exit_node="end")

def test_early_stop_propagation(mock_engine: MagicMock, graph_context: GraphContext):
    """If a node returns stop=True, execution should halt immediately."""
    mock_engine.execute_ephemeral.return_value = make_response("Output")
    
    class StopNode(LLMNode):
        def execute(self, context):
            # Overrides execute, does not call the engine
            return NodeResult(success=True, outputs={self._output_key: "Stopped"}, stop=True)
            
    nodes = {
        "a": StopNode("a", "A", mock_engine, PlannerConfig()),
        "b": LLMNode("b", "B", mock_engine, PlannerConfig())
    }
    edges = [ExecutionEdge(source="a", target="b")]
    graph = ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="b")
    
    executor = GraphExecutor()
    result = executor.run(graph, graph_context)
    
    assert result.outputs["a"] == "Stopped"
    # Node B should never execute, so the engine should only be called if Node A called it (which it doesn't)
    mock_engine.execute_ephemeral.assert_not_called()

def test_graph_trace_events_emitted(mock_engine: MagicMock, graph_context: GraphContext):
    """Verify GRAPH_STARTED, NODE_STARTED, NODE_FINISHED, and GRAPH_FINISHED are emitted."""
    mock_engine.execute_ephemeral.return_value = make_response("Output")
    
    nodes = {"n1": LLMNode("n1", "Prompt", mock_engine, PlannerConfig())}
    graph = ExecutionGraph(nodes=nodes, edges=[], entry_node="n1", exit_node="n1")
    
    executor = GraphExecutor()
    executor.run(graph, graph_context)
    
    event_types = [e.event_type for e in graph_context.trace.events]
    
    assert TraceEventType.GRAPH_STARTED in event_types
    assert TraceEventType.NODE_STARTED in event_types
    assert TraceEventType.NODE_FINISHED in event_types
    assert TraceEventType.GRAPH_FINISHED in event_types

def test_graph_validation_missing_entry():
    nodes = {"n1": LLMNode("n1", "A", MagicMock(), PlannerConfig())}
    with pytest.raises(ValueError, match="Entry node 'missing' not found"):
        ExecutionGraph(nodes=nodes, edges=[], entry_node="missing", exit_node="n1")

def test_graph_validation_multiple_entries():
    mock_eng = MagicMock()
    nodes = {
        "a": LLMNode("a", "A", mock_eng, PlannerConfig()),
        "b": LLMNode("b", "B", mock_eng, PlannerConfig()),
        "c": LLMNode("c", "C", mock_eng, PlannerConfig())
    }
    edges = [
        ExecutionEdge(source="a", target="c"),
        ExecutionEdge(source="b", target="c")
    ]
    with pytest.raises(ValueError, match="exactly one entry node"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="c")

def test_graph_validation_orphan_node():
    """Should fail if there is an unreachable node. 
    Note: An acyclic disconnected component implies multiple roots, which fails the entry check.
    To test reachability specifically, we need a graph with 1 root, 1 leaf, no cycles, but an orphan.
    This is mathematically impossible in a simple DAG without multiple edges, so we test a disconnected cycle instead,
    which will be caught by the cycle check. We adjust the expected match to 'contains a cycle'."""
    mock_eng = MagicMock()
    nodes = {
        "a": LLMNode("a", "A", mock_eng, PlannerConfig()),
        "b": LLMNode("b", "B", mock_eng, PlannerConfig()),
        "c": LLMNode("c", "C", mock_eng, PlannerConfig()),
        "d": LLMNode("d", "D", mock_eng, PlannerConfig())
    }
    # "c" and "d" form a cycle, disconnected from "a" and "b"
    edges = [
        ExecutionEdge(source="a", target="b"),
        ExecutionEdge(source="c", target="d"),
        ExecutionEdge(source="d", target="c")
    ]
    with pytest.raises(ValueError, match="contains a cycle"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="b")

def test_graph_validation_self_loop():
    mock_eng = MagicMock()
    nodes = {"a": LLMNode("a", "A", mock_eng, PlannerConfig())}
    edges = [ExecutionEdge(source="a", target="a")]
    with pytest.raises(ValueError, match="Self-loop detected"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="a")

def test_graph_validation_duplicate_edge():
    mock_eng = MagicMock()
    nodes = {
        "a": LLMNode("a", "A", mock_eng, PlannerConfig()),
        "b": LLMNode("b", "B", mock_eng, PlannerConfig())
    }
    edges = [
        ExecutionEdge(source="a", target="b"),
        ExecutionEdge(source="a", target="b")
    ]
    with pytest.raises(ValueError, match="Duplicate edge detected"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="b")

def test_graph_validation_invalid_exit():
    """Should fail if there are multiple exit nodes (out_degree == 0)."""
    mock_eng = MagicMock()
    nodes = {
        "a": LLMNode("a", "A", mock_eng, PlannerConfig()),
        "b": LLMNode("b", "B", mock_eng, PlannerConfig()),
        "c": LLMNode("c", "C", mock_eng, PlannerConfig())
    }
    # 'b' and 'c' are both leaves
    edges = [
        ExecutionEdge(source="a", target="b"),
        ExecutionEdge(source="a", target="c")
    ]
    with pytest.raises(ValueError, match="exactly one exit node"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="b")

def test_graph_validation_entry_equals_exit_multi_node():
    mock_eng = MagicMock()
    nodes = {
        "a": LLMNode("a", "A", mock_eng, PlannerConfig()),
        "b": LLMNode("b", "B", mock_eng, PlannerConfig())
    }
    edges = [ExecutionEdge(source="a", target="b")]
    with pytest.raises(ValueError, match="Entry and exit nodes cannot be the same"):
        ExecutionGraph(nodes=nodes, edges=edges, entry_node="a", exit_node="a")

def test_node_exception_propagation(mock_engine: MagicMock, graph_context: GraphContext):
    """If a node raises an exception, graph should raise GraphExecutionError and emit GRAPH_FINISHED."""
    class CrashNode(LLMNode):
        def execute(self, context):
            raise RuntimeError("Node crashed!")
            
    nodes = {"n1": CrashNode("n1", "A", mock_engine, PlannerConfig())}
    graph = ExecutionGraph(nodes=nodes, edges=[], entry_node="n1", exit_node="n1")
    
    executor = GraphExecutor()
    
    with pytest.raises(GraphExecutionError, match="Node 'n1' failed") as exc_info:
        executor.run(graph, graph_context)
        
    assert exc_info.value.node_id == "n1"
    assert isinstance(exc_info.value.original, RuntimeError)
    assert isinstance(exc_info.value.blackboard_snapshot, dict)
    
    event_types = [e.event_type for e in graph_context.trace.events]
    assert TraceEventType.GRAPH_STARTED in event_types
    assert TraceEventType.NODE_STARTED in event_types
    assert TraceEventType.NODE_FINISHED in event_types
    assert TraceEventType.GRAPH_FINISHED in event_types

def test_blackboard_merge_coexistence(graph_context: GraphContext):
    """Ensure multiple distinct keys survive on the blackboard."""
    graph_context.blackboard.update({"summary": "initial summary"})
    graph_context.blackboard.update({"critique": "initial critique"})
    
    assert graph_context.blackboard.get("summary") == "initial summary"
    assert graph_context.blackboard.get("critique") == "initial critique"

def test_blackboard_merge_overwrite_collision(graph_context: GraphContext):
    """Ensure later updates overwrite earlier keys with the same name."""
    graph_context.blackboard.update({"text": "initial"})
    graph_context.blackboard.update({"text": "overwritten"})
    
    assert graph_context.blackboard.get("text") == "overwritten"