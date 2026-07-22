Hermes uses a tiered, pipeline-based memory system to maintain persistent, reusable knowledge.

## 1. UnifiedMemoryManager (Facade)
The single entry point for the runtime. Routes `remember()` and `recall()` operations to underlying backends based on `MemoryTier` (EPISODIC, SEMANTIC).

## 2. Storage Backends (Protocols)
Decoupled from the manager via `EpisodicStore` and `SemanticStore` protocols.
- **Episodic**: SQLite or In-Memory substring search.
- **Semantic**: Vector stores using `EmbeddingProvider` (e.g., InMemoryVectorStore).

## 3. Retrieval Models
- `RetrievedMemory`: Runtime representation of a memory (id, tier, content, score).
- `RetrievedContext`: Passed to `PlannerState`, contains a list of memories and metadata (e.g., `semantic_available`).

## 4. Memory Pipeline
Retrieval is processed through an extensible `MemoryPipeline`:
`Deduplicator -> Ranker -> TokenBudgetCompressor -> Summarizer`

Each stage implements the `MemoryStage` protocol (`process(memories) -> memories`).

## 5. Planner Ownership
Planners do not write to memory directly. They emit `MemoryCandidate` objects in `AgentResult`. A future persistence service will process these candidates.
---

### FILE 3: `docs/architecture/03_memory.md` (NEW)

```markdown
# Memory Architecture

Hermes uses a tiered, pipeline-based memory system to maintain persistent, reusable knowledge.

## 1. UnifiedMemoryManager (Facade)
The single entry point for the runtime. Routes `remember()` and `recall()` operations to underlying backends based on `MemoryTier` (EPISODIC, SEMANTIC).

## 2. Storage Backends (Protocols)
Decoupled from the manager via `EpisodicStore` and `SemanticStore` protocols.
- **Episodic**: SQLite or In-Memory substring search.
- **Semantic**: Vector stores using `EmbeddingProvider` (e.g., InMemoryVectorStore).

## 3. Retrieval Models
- `RetrievedMemory`: Runtime representation of a memory (id, tier, content, score).
- `RetrievedContext`: Passed to `PlannerState`, contains a list of memories and metadata (e.g., `semantic_available`).

## 4. Memory Pipeline
Retrieval is processed through an extensible `MemoryPipeline`:
`Deduplicator -> Ranker -> TokenBudgetCompressor -> Summarizer`

Each stage implements the `MemoryStage` protocol (`process(memories) -> memories`).

## 5. Planner Ownership
Planners do not write to memory directly. They emit `MemoryCandidate` objects in `AgentResult`. A future persistence service will process these candidates.