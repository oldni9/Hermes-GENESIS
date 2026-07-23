# Versioning & Compatibility Policy

The Hermes Runtime API uses Semantic Versioning (`Major.Minor.Patch`) to manage changes to the API contract. 

## Schema Versioning

Every event and REST response contains a `schema_version` string. The current baseline is `"1.0.0"`.

## Change Classifications

### Patch Updates (e.g., 1.0.0 -> 1.0.1)
* Bug fixes in API logic.
* Documentation updates.
* Performance optimizations.
* **Client Impact**: None. No code changes required.

### Minor Updates (e.g., 1.0.0 -> 1.1.0)
* Addition of new optional fields to existing payloads.
* Addition of new REST endpoints.
* Addition of new WebSocket event types.
* **Client Impact**: Clients should write deserializers that ignore unknown fields to remain forward-compatible. No breaking changes to existing logic.

### Major Updates (e.g., 1.0.0 -> 2.0.0)
* Removal or renaming of existing fields.
* Changes to data types (e.g., string to int).
* Changes to WebSocket connection lifecycle or replay protocol semantics.
* **Client Impact**: Clients must update their code to support the new contract. 

## Schema Version Validation Policy (Strict)

**Note:** The Hermes Runtime Serializer currently implements a **strict** schema version validation policy.

If a client or event store attempts to deserialize an event with a `schema_version` that does not exactly match the runtime's current `SCHEMA_VERSION` constant (e.g., server is `1.0.1`, event is `1.0.0`), the serializer will raise a `SerializationError`.

**Rationale**: During the v1.0.0 freeze phase, this strictness guarantees that no subtle serialization drift occurs between the backend and any connected clients (like the Tauri UI). 

**Future Evolution**: In future major releases, this policy may be relaxed to accept matching major versions (e.g., `1.x.x`), but for the initial freeze, exact matching is enforced to ensure absolute contract stability.

## Frontend Compatibility Expectations

The Desktop UI (Sprint 17B) will be built against `v1.0.0`. 
* The UI must gracefully ignore unknown event types or payload fields to ensure compatibility with future minor server updates.
* The UI must fail gracefully if an expected field is missing, logging a warning rather than crashing.

## Deprecation Policy

If a field or endpoint is marked for removal:
1. It will be marked as `@deprecated` in the documentation.
2. It will remain functional for one full minor release cycle.
3. It will be removed in the subsequent major release.