# Hermes Request Flow

> Last Updated: After PR4

This document describes how a single user request travels through Hermes.

---

# Current Request Flow

```
User Request
      │
      ▼
AI Pipeline
      │
      ▼
Planner
      │
      ▼
Plan
      │
      ▼
PlanToExecutionPlanAdapter
      │
      ▼
Capability
      │
      ▼
PlanExecutor
      │
      ▼
ExecutionService
      │
      ▼
ProviderManager
      │
      ▼
Selected Provider
      │
      ▼
ProviderResult
```

---

# Step 1

User submits a request.

Example

```
Write a Python web scraper.
```

No provider has been selected yet.

---

# Step 2

Planner

Input

```
Raw prompt
```

Output

```
Plan
```

Example

```
Plan

Step 1
Domain:
CODE

Instruction:
Write scraper
```

Planning determines *what* should happen.

---

# Step 3

Capability Resolution

Component

```
PlanToExecutionPlanAdapter
```

Input

```
Plan
```

Output

```
CapabilityType.CODE
```

No provider selection happens here.

Only capability classification.

---

# Step 4

Execution Planning

Component

```
PlanExecutor
```

Input

```
Plan
```

Behavior

Iterates over every PlanStep.

For each step

```
Domain

↓

CapabilityType

↓

ExecutionService.execute()
```

---

# Step 5

Execution

ExecutionService receives

```
Prompt

CapabilityType
```

Example

```
Prompt

Write scraper

Capability

CODE
```

ExecutionService does not perform planning.

---

# Step 6

Provider Selection

ProviderManager selects

```
Best Provider
```

Example

```
CapabilityType.CODE

↓

Groq
```

or

```
CapabilityType.CODE

↓

OpenRouter
```

Selection depends on registry configuration.

---

# Step 7

Provider Execution

Provider executes request.

Returns

```
ProviderResult
```

---

# Step 8

Result

Returned to caller.

Example

```
ProviderResult

success=True

text="..."
```

---

# Current Architecture

```
Planner

↓

Capability

↓

Execution

↓

Provider
```

Every layer has one responsibility.

---

# Future Request Flow

PR5+

```
Planner

↓

Workflow Engine

↓

Agent

↓

Execution

↓

Provider
```

Workflow will coordinate:

- retries
- branching
- dependencies
- loops

without changing Planning.

---

# Long-Term Vision

```
User

↓

Pipeline

↓

Planner

↓

Workflow

↓

Agent

↓

Execution

↓

Provider

↓

Response
```

Each layer remains independently testable.

No layer bypasses another.

---

# Core Principle

Planning decides

```
What should happen?
```

Capability decides

```
What kind of task is this?
```

Execution decides

```
Run the task.
```

Providers decide

```
How to produce the output.
```

Keeping these responsibilities separate is the foundation of Hermes.