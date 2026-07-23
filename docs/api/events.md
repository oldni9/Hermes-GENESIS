# Runtime Event Catalog

All events inherit from `BaseEvent` and include the following fields:
* `event_type` (str): Discriminator for the event subclass.
* `execution_id` (str): The unique ID of the execution.
* `timestamp` (float): Unix timestamp of event creation.
* `schema_version` (str): Semantic version of the event schema (e.g., `"1.0.0"`).
* `sequence` (int): Monotonically increasing sequence number per execution.
* `payload` (dict): Event-specific data.

---

## ExecutionStartedEvent
Emitted when an execution transitions from `queued` to `running`.
* `event_type`: `"execution_started"`
* **Terminal**: No
* **Payload**:
  ```json
  { "prompt": "Write a hello world script." }