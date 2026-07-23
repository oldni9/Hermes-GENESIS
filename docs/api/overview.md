Hermes Runtime API Overview
The Hermes Runtime API is the stable, transport-agnostic interface for interacting with the Hermes AI Operating Environment. It decouples the execution core (Planners, Graphs, Memory) from clients (Desktop UI, CLI, Web Dashboards).

API Philosophy
Transport Separation: REST is used for stateless control plane operations (starting executions, fetching snapshots, metrics). WebSockets are used for the data plane (streaming live execution events and traces).
Typed Events: All WebSocket streams emit strictly typed Pydantic models serialized as JSON. Clients should use the event_type field as a discriminator for deserialization.
Immutability: Execution state and trace events are immutable once published. Clients can safely cache events.
Versioning Policy
All events and REST payloads include a schema_version string (e.g., "1.0.0").

Major (x.0.0): Breaking changes (removed fields, changed types). Requires client updates.
Minor (1.x.0): Additive changes (new optional fields, new event types). Non-breaking.
Patch (1.0.x): Bug fixes, documentation updates.
This documentation freezes the API contract at v1.0.0.

Execution Lifecycle
Client sends POST /v1/execute with a prompt.
API returns execution_id and status: "queued".
Client opens WebSocket to /ws/execution/{execution_id}.
ExecutionManager assigns the task to an ExecutionWorker thread.
Worker executes the AgentExecutor, streaming TraceRuntimeEvents via the bus.
Client visualizes the trace in real-time.
Worker finishes, emitting ExecutionFinishedEvent or ExecutionFailedEvent.
WebSocket connection closes cleanly.
Architecture Flow
POST /v1/execute        │        ▼ExecutionManager        │ExecutionWorker        │AgentExecutor        │TraceEvents        │RuntimeEventBus ──► ExecutionEventStore (Ring Buffer)        │WebSocket Clients
Error Handling Conventions
REST: Standard HTTP status codes (200, 202, 404, 500). Error bodies are JSON: {"detail": "Error message"}.
WebSocket: If an execution fails, an ExecutionFailedEvent is emitted containing the error string in the payload, followed by socket closure.