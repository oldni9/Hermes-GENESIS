Hermes is an AI Operating Environment designed to orchestrate complex, long-running reasoning tasks. It is not an LLM wrapper; it is a runtime for AI agents.

---

**1. Introduction**

Hermes provides a modular, layered architecture that separates concerns across lifecycle management, execution mechanics, strategy, orchestration, memory, tooling, isolation, and provider abstraction. Each subsystem is independently replaceable while working in concert to enable autonomous, long-running agentic workflows.

---

**2. Core Subsystems**

**2.1 Runtime (hermes/core/runtime.py)**  
- The lifecycle layer.  
- Enforces execution limits via `RuntimePolicy`.  
- Tracks usage metrics via `RuntimeMetrics`.  
- Handles cancellation via `CancellationToken`.

**2.2 Execution Engine (hermes/agent/executor/engine.py)**  
- The stateless mechanics layer.  
- Owns LLM calls, tool execution, and policy enforcement.  
- Exposes:  
  - `execute_turn()` – for a single agent turn with full context.  
  - `execute_ephemeral()` – for short-lived, stateless invocations.

**2.3 Planner Architecture (hermes/agent/executor/planners/)**  
- The strategy layer.  
- Planners (ReAct, Tree of Thoughts, Debate, etc.) orchestrate the engine.  
- Registered globally via `PlannerRegistry`.

**2.4 Execution Graph (docs/architecture/02_execution_graph.md)**  
- The orchestration layer.  
- Defines DAGs of nodes (LLM, Tool, Planner) for declarative workflow composition.

**2.5 Unified Memory (docs/architecture/03_memory.md)**  
- The persistence and retrieval layer.  
- Facade over:  
  - Episodic memory (SQLite).  
  - Semantic memory (Vector store).  
- Includes a processing pipeline for memory operations.

**2.6 Tool System (docs/architecture/05_tools.md)**  
- The capability layer.  
- `ToolManager` and `ToolRegistry` manage sandboxed, namespaced function calling.

**2.7 Workspace (docs/architecture/07_workspace.md)**  
- The isolation layer.  
- Provides sandboxed filesystems and environments for autonomous coding tasks.

**2.8 AI Pipeline (docs/architecture/06_ai.md)**  
- The provider abstraction layer.  
- Routes requests via `AIOrchestrator` and `AIPipeline` to multiple LLM providers.
