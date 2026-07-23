
---

### FILE 2: `docs/api/rest.md` (NEW)

```markdown
# REST API Reference

Base URL: `http://localhost:8000`

## Health & Metrics

### `GET /health`
Checks if the API server is running.
* **Status Codes**: 200 OK
* **Response**: `{"status": "ok"}`

### `GET /metrics`
Retrieves aggregated runtime metrics for observability dashboards.
* **Status Codes**: 200 OK
* **Response Schema**:
  ```json
  {
    "executions": {
      "queued": 0, "running": 1, "completed": 5, "failed": 0, "cancelled": 0,
      "average_runtime": 4.52
    },
    "event_bus": {
      "subscribers": 1, "dropped_events": 0, "published_events": 142
    },
    "thread_pool": {
      "max_workers": 4, "queued_jobs": 0
    },
    "event_store": {
      "ring_buffer_keys": 6, "replay_hits": 1, "replay_misses": 0
    }
  }


Execution Management
POST /v1/execute
Creates a new agent execution and queues it for processing.

Status Codes:

200 OK: Execution created and queued.

Request Schema:

json
{
  "prompt": "Write a hello world script in Python.",
  "system_prompt": "You are a helpful coding assistant." // Optional
}
Response Schema:

json
{
  "execution_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "queued"
}
Idempotency: Not idempotent. Calling twice creates two separate executions.

GET /v1/execute/{execution_id}
Retrieves the current snapshot of an execution. Used for reconnect logic.

Status Codes:

200 OK: Snapshot retrieved.

404 Not Found: Execution ID does not exist.

Response Schema:

json
{
  "execution_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "result": null,
  "error": null,
  "last_event_sequence": 42,
  "created_at": 1698765432.123,
  "updated_at": 1698765435.456
}
POST /v1/execute/{execution_id}/cancel
Requests cancellation for a running execution.

Status Codes:

200 OK: Cancellation request received (returns cancelled: false if already finished).

404 Not Found: Execution ID does not exist.

Response Schema:

json
{
  "execution_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "cancelled": true
}