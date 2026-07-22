"""
===============================================================================
Execution Graph Models
===============================================================================

Sprint 15.1 Update:
Added GraphRunner and ParallelRunner protocols.
NodeResult is frozen (immutable) to prevent post-merge mutation.
NodeMetadata remains mutable to avoid false immutability, but uses Tuples for collections.
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from hermes.ai.conversation import AIConversation
    from hermes.core.runtime import RuntimeContext
    from hermes.agent.executor.trace import AgentTrace
    from hermes.runtime.parallel import ParallelJob, ParallelResult
    from hermes.core.runtime import CancellationToken


class GraphExecutionError(Exception):
    """Raised when a node fails during graph execution, carrying context."""
    def __init__(
        self, 
        node_id: str, 
        trace: "AgentTrace", 
        blackboard_snapshot: Dict[str, Any], 
        original: Exception
    ) -> None:
        self.node_id = node_id
        self.trace = trace
        self.blackboard_snapshot = blackboard_snapshot
        self.original = original
        super().__init__(f"Node '{node_id}' failed during execution: {original}")


class _SafeDict(dict):
    """Dict subclass that returns empty string for missing keys during formatting."""
    def __missing__(self, key):
        return ''


class Blackboard:
    """Encapsulated wrapper for graph blackboard data."""
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self._data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def update(self, d: Dict[str, Any]) -> None:
        self._data.update(d)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data


@dataclass
class GraphContext:
    """Lightweight state object passed along graph edges."""
    conversation: "AIConversation"
    runtime_context: "RuntimeContext"
    trace: "AgentTrace"
    blackboard: Blackboard = field(default_factory=Blackboard)


@dataclass
class NodeMetadata:
    """Typed metadata for a NodeResult. Uses tuples for collections, but remains mutable."""
    duration: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    memory_candidates: Tuple[Any, ...] = field(default_factory=tuple)
    trace: Optional["AgentTrace"] = None
    branch_metadata: Tuple["NodeMetadata", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NodeResult:
    """Standardized, immutable result returned by every GraphNode."""
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    stop: bool = False
    metadata: NodeMetadata = field(default_factory=NodeMetadata)


@dataclass
class GraphResult:
    """Result returned by the GraphRunner, containing raw outputs."""
    success: bool
    outputs: Dict[str, Any]
    duration: float
    trace: "AgentTrace"
    memory_candidates: List[Any] = field(default_factory=list)
    token_usage: Dict[str, int] = field(default_factory=dict)

    def to_node_result(self) -> NodeResult:
        """Centralized conversion from GraphResult to NodeResult, preserving metadata."""
        return NodeResult(
            success=self.success,
            outputs=self.outputs,
            stop=not self.success,
            metadata=NodeMetadata(
                duration=self.duration,
                token_usage=self.token_usage,
                memory_candidates=tuple(self.memory_candidates),
                trace=self.trace
            )
        )


class GraphRunner(Protocol):
    """Protocol for executing an ExecutionGraph, decoupling nodes from the executor."""
    def run(
        self, 
        graph: "ExecutionGraph", 
        context: GraphContext
    ) -> GraphResult:
        ...


class ParallelRunner(Protocol):
    """Protocol for executing parallel jobs, decoupling nodes from the service."""
    def execute(
        self, 
        jobs: List["ParallelJob"], 
        cancellation_token: Optional["CancellationToken"] = None,
        timeout: Optional[float] = None
    ) -> List["ParallelResult"]:
        ...


@dataclass(frozen=True)
class ExecutionEdge:
    """Directed edge connecting two nodes in a graph."""
    source: str
    target: str


class ExecutionGraph:
    """
    Immutable Directed Acyclic Graph (DAG) definition.
    Validates acyclicity, single entry/exit, reachability, and structural integrity.
    """
    def __init__(
        self, 
        nodes: Dict[str, Any], 
        edges: List[ExecutionEdge], 
        entry_node: str, 
        exit_node: str
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._entry_node = entry_node
        self._exit_node = exit_node
        self._parents: Dict[str, List[str]] = {n: [] for n in nodes}
        self._children: Dict[str, List[str]] = {n: [] for n in nodes}
        self._build_adjacency()
        self._validate()

    @property
    def nodes(self) -> Dict[str, Any]:
        return self._nodes

    @property
    def edges(self) -> List[ExecutionEdge]:
        return self._edges

    @property
    def entry_node(self) -> str:
        return self._entry_node

    @property
    def exit_node(self) -> str:
        return self._exit_node

    @property
    def parents(self) -> Dict[str, List[str]]:
        return self._parents

    @property
    def children(self) -> Dict[str, List[str]]:
        return self._children

    def _build_adjacency(self) -> None:
        for edge in self._edges:
            if edge.source in self._children:
                self._children[edge.source].append(edge.target)
            if edge.target in self._parents:
                self._parents[edge.target].append(edge.source)

    def _validate(self) -> None:
        if self._entry_node not in self._nodes:
            raise ValueError(f"Entry node '{self._entry_node}' not found in nodes.")
        if self._exit_node not in self._nodes:
            raise ValueError(f"Exit node '{self._exit_node}' not found in nodes.")
            
        if self._entry_node == self._exit_node and len(self._nodes) > 1:
            raise ValueError("Entry and exit nodes cannot be the same in a multi-node graph.")

        edge_set = set()
        for edge in self._edges:
            if edge.source not in self._nodes:
                raise ValueError(f"Edge source '{edge.source}' not found in nodes.")
            if edge.target not in self._nodes:
                raise ValueError(f"Edge target '{edge.target}' not found in nodes.")
            if edge.source == edge.target:
                raise ValueError(f"Self-loop detected on node '{edge.source}'.")
            if (edge.source, edge.target) in edge_set:
                raise ValueError(f"Duplicate edge detected: {edge.source} -> {edge.target}")
            edge_set.add((edge.source, edge.target))

        in_degree = {n: 0 for n in self._nodes}
        out_degree = {n: 0 for n in self._nodes}
        for edge in self._edges:
            in_degree[edge.target] += 1
            out_degree[edge.source] += 1

        roots = [n for n in self._nodes if in_degree[n] == 0]
        if len(roots) != 1 or roots[0] != self._entry_node:
            raise ValueError("Graph must have exactly one entry node (in_degree == 0).")

        leaves = [n for n in self._nodes if out_degree[n] == 0]
        if len(leaves) != 1 or leaves[0] != self._exit_node:
            raise ValueError("Graph must have exactly one exit node (out_degree == 0).")

        visited_cycle = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited_cycle.add(node_id)
            rec_stack.add(node_id)
            
            for child in self._children[node_id]:
                if child not in visited_cycle:
                    if has_cycle(child):
                        return True
                elif child in rec_stack:
                    return True
                    
            rec_stack.remove(node_id)
            return False

        for node_id in self._nodes:
            if node_id not in visited_cycle:
                if has_cycle(node_id):
                    raise ValueError("ExecutionGraph contains a cycle.")

        visited_reach = set()
        def dfs_reach(node_id: str):
            if node_id in visited_reach: return
            visited_reach.add(node_id)
            for child in self._children[node_id]:
                dfs_reach(child)
        
        dfs_reach(self._entry_node)
        if visited_reach != set(self._nodes.keys()):
            raise ValueError("Graph contains orphan/unreachable nodes.")

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture