# Execution Graph Architecture

The Execution Graph subsystem transforms Hermes from a framework with isolated planner classes into a universal orchestrator of reasoning workflows.

## Core Concepts

### 1. GraphNode (Abstract Base Class)
Nodes are the fundamental units of work in a graph. Instead of an enum, nodes use polymorphism. 
All nodes must implement:
```python
def execute(self, context: GraphContext, engine: ExecutionEngine, config: PlannerConfig) -> NodeResult
```

**Node Subclasses:**
- `LLMNode`: Executes a prompt via the ExecutionEngine.
- `ToolNode`: Executes a specific tool.
- `MemoryNode`: Queries the UnifiedMemoryManager.
- `PlannerNode`: Wraps an existing `Planner` (e.g., `ReActPlanner`).
- `JudgeNode`: Synthesizes inputs from multiple parent nodes.

### 2. NodeResult
Every node returns a standardized `NodeResult` dataclass:
- `success: bool`
- `outputs: dict[str, Any]`: Data left on the blackboard for downstream nodes.
- `stop: bool`: If True, halts graph execution immediately.

### 3. GraphContext
The state object passed along the edges. Kept intentionally small:
- `conversation`: The shared `ConversationState`.
- `runtime`: The `RuntimeContext` (policy, metrics, token).
- `trace`: The `AgentTrace` for telemetry.
- `blackboard`: A `dict` for nodes to pass arbitrary data to downstream nodes.

### 4. ExecutionEdge
Explicit edge objects connecting nodes.
```python
@dataclass
class ExecutionEdge:
    source: str
    target: str
    # Future: conditions, weights, failure routing
```

### 5. ExecutionGraph
The DAG definition. Contains nodes and edges. Validates acyclicity on initialization.

## Execution Flow

1. `AgentExecutor` receives an `ExecutionPlan` (which wraps an `ExecutionGraph`).
2. `GraphExecutor` performs a topological sort of the nodes.
3. Nodes are executed sequentially (Sprint 14). Parallel fan-out is deferred to Sprint 15.
4. `NodeResult.outputs` are merged into `GraphContext.blackboard`.
5. Upon reaching the exit node, the final result is returned as an `AgentResult`.
