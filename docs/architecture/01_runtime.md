**Runtime Architecture**

The Runtime layer enforces execution safety and provides deterministic telemetry.

---

**1. RuntimePolicy (Immutable)**  
Defines the constraints of an execution:
- `timeout` – Maximum duration in seconds.
- `max_tokens` – Maximum total tokens (prompt + completion).
- `max_parallel_workers` – Concurrency limit for parallel planners.

---

**2. RuntimeMetrics (Thread-Safe)**  
Tracks actual usage during execution:
- Token counts – `used_prompt_tokens` and `used_completion_tokens`.
- Iteration counts – `iterations`, `planner_iterations`, and `execution_turns`.
- Cost tracking – monitors usage-based costs.
- Uses `threading.Lock` to ensure thread-safe updates during parallel execution.

---

**3. CancellationToken**  
A cooperative cancellation primitive. Planners and the ExecutionEngine check `token.cancelled` at loop boundaries to gracefully abort execution when requested.

---

**4. AgentTrace (Thread-Safe)**  
Records `TraceEvent` objects with sequence numbers and thread IDs for deterministic UI replay.  
Events include:
- `POLICY_CHECK`
- `TOT_BRANCH_SELECTED`
- `PARALLEL_STARTED`

---

**5. HermesRuntimeError**  
Structured exceptions raised by the engine and caught by planners to cleanly terminate execution.  
Includes:
- `DeadlineExceeded` – when the timeout is reached.
- `BudgetExceeded` – when token or cost limits are exceeded.
- `ExecutionCancelled` – when cancellation is triggered via `CancellationToken`.