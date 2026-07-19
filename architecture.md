# Hermes Architecture

> Last Updated: After PR4 (Planning → Execution Integration)

---

# High-Level Overview

Hermes follows a layered architecture.

Each layer has one responsibility.

No layer reaches around another.

```
                ┌────────────────────────────┐
                │          User              │
                └────────────┬───────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │        AI Pipeline         │
                └────────────┬───────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │         Planner            │
                └────────────┬───────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │            Plan            │
                └────────────┬───────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     PlanToExecutionPlanAdapter      PlanExecutor
              │                             │
              ▼                             ▼
        CapabilityResolver          ExecutionService
              │                             │
              ▼                             ▼
         CapabilityRegistry         ProviderManager
                                            │
                                            ▼
                                   Provider Implementations
```

---

# Layer Responsibilities

## Bootstrap

Responsible for application startup.

Owns:

- configuration loading
- dependency creation
- service registration
- runtime initialization

Does NOT execute AI requests.

---

## Runtime

Coordinates global services.

Responsible for:

- lifecycle
- configuration
- logging
- service registry

---

## Intelligence

Produces structured reasoning objects.

Contains:

- Intent
- ExecutionPlan

It never talks directly to providers.

---

## Capability Layer

Responsible for deciding

"What capability is required?"

Examples:

- CHAT
- CODE
- WEB
- IMAGE
- AUDIO

Capability resolution is provider-independent.

---

## Planning Layer

Responsible for

"How should this task be performed?"

Produces:

- Plan
- PlanStep

Planning is intentionally unaware of providers.

---

## Execution Layer

Responsible for executing work.

Owns:

- ExecutionService
- ExecutionEngine
- ExecutionContext

Execution never performs planning.

---

## Provider Layer

Responsible for model interaction.

Examples:

- Groq
- Cerebras
- OpenRouter
- Mistral
- Ollama
- LM Studio

Providers never know about Planning.

---

# Integration Points

Current integrations:

## PR3

Planning

↓

Capability

Implemented by:

PlanToExecutionPlanAdapter

Purpose:

Convert a Plan into an ExecutionPlan and resolve the correct Capability.

---

## PR4

Planning

↓

Execution

Implemented by:

PlanExecutor

Purpose:

Execute every PlanStep using ExecutionService.

---

# Dependency Rules

Allowed

Planning
→ Capability

Planning
→ Execution

Execution
→ Providers

Capability
→ Intelligence

Forbidden

Provider
→ Planning

Provider
→ Capability

Execution
→ Planner

Planner
→ ProviderManager

Capability
→ Provider

Planning
→ Provider

These rules keep Hermes modular.

---

# Current Status

Completed

- Bootstrap
- Runtime
- Providers
- Intelligence
- Capability
- Planning
- PR3
- PR4

Upcoming

- Workflow
- Agent
- Memory
- Multi-step orchestration
- Autonomous execution

---

# Design Principles

Hermes follows:

- Dependency Injection
- Composition over inheritance
- Provider agnostic architecture
- Layer isolation
- Public API usage only
- Strict backwards compatibility
- No circular dependencies
- Test-first integrations

---

# Future Direction

Planned execution flow:

```

User
↓
Pipeline
↓
Planner
↓
Plan
↓
Capability Adapter
↓
Plan Executor
↓
Workflow Engine
↓
Agent
↓
Execution Service
↓
Provider
↓
Result

```

The Workflow and Agent layers will extend this flow without breaking previous integrations.