# Hermes Genesis – Technical Debt

This document tracks improvements that are intentionally postponed.

These are NOT blockers.

The codebase is considered production-ready unless an item is explicitly promoted to Critical.

---

# Rules

Priority levels

P0 = Critical (must fix immediately)

P1 = Should be addressed before release

P2 = Improvement

P3 = Nice to have

Unless marked P0, implementation work should continue.

---

# Current Status

Current Sprint:
Sprint 5

Current Phase:
Foundation

Current Test Status:
105 / 105 tests passing

Architecture Status:
Stable

---

# Content System

## P2 – Metadata Hash Cache

Status:
Deferred

Description

Every Content subclass computes metadata hashes repeatedly.

Introduce a cached hash implementation for immutable content objects.

Reason

Performance optimization only.

No functional issue.

---

## P2 – File Encoding Enum

Status:
Deferred

Current

encoding="hex"

Future

Introduce

FileEncoding(Enum)

Values

- HEX
- BASE64
- UTF8

Reason

Cleaner API.

Current implementation works correctly.

---

## P2 – Validator Consistency

Status:
Deferred

Review validator exception types.

Some validators raise ValueError where TypeError may be more appropriate.

Only perform after test suite expansion.

---

## P2 – Registry Stress Tests

Status:
Deferred

Factory registry should receive multithreaded stress tests.

Current locking implementation is sufficient.

---

## P2 – FileContent Edge Cases

Status:
Deferred

Additional tests

- malformed hex
- invalid encoding
- invalid source combinations
- corrupted serialized payload

Current implementation already passes all required tests.

---

## P2 – Equality Review

Status:
Deferred

Review whether Content base class should define equality semantics or allow dataclass-generated equality.

Current implementation is correct.

---

## P3 – Serialization Optimizations

Status:
Deferred

Potential improvements

- avoid repeated json.dumps

- optional serializer backend

- faster hashing

---

# Promotion Rules

An item becomes P0 only if

- causes failing tests

- causes data corruption

- breaks architecture

- blocks future implementation

Otherwise leave deferred.

---

Last Updated

Sprint 5 PR1