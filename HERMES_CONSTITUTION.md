# Hermes Genesis — Architecture Constitution

> Version: Living Document
> Status: Canonical Project Context
> Last Updated: Sprint 8
>
> This document is the authoritative architectural guide for Hermes Genesis.
>
> Every AI assistant and every developer contributing to Hermes **must read this document before making architectural decisions.**
>
> The purpose of this document is to preserve long-term architectural consistency regardless of which AI model or developer continues the project.

---

# 1. Vision

Hermes Genesis is **NOT** a chatbot.

Hermes Genesis is an **Autonomous AI Runtime** that will eventually become:

- Autonomous AI Runtime
- Developer Platform
- Native Desktop Application
- Custom Terminal
- Intelligent Workspace
- Autonomous Coding Assistant
- Modular AI Operating Environment

The long-term goal is to build an AI system capable of reasoning, planning, executing, debugging, reflecting, and interacting with the user's computer through a transparent execution environment.

---

# 2. Core Philosophy

Hermes values architecture over shortcuts.

Every new feature must strengthen the architecture rather than weaken it.

Hermes follows these principles:

- SOLID
- Dependency Inversion
- Composition over Inheritance
- Explicit Interfaces
- Strict Separation of Concerns
- Provider Agnostic
- Planner Agnostic
- UI Agnostic
- Tool Agnostic
- Workspace Aware
- Highly Observable
- Long-term Maintainability

The architecture always takes precedence over convenience.

---

# 3. What Hermes Is NOT

Hermes will never intentionally become:

❌ Another ChatGPT wrapper

❌ A VS Code extension

❌ A terminal wrapper

❌ A collection of scripts

❌ A provider-specific framework

❌ A tightly coupled monolithic application

If an implementation moves Hermes toward one of these, it should be rejected.

---

# 4. Long-Term Roadmap

---

## Phase 0 — Foundation

Completed

- Repository
- Configuration
- Logging
- Bootstrap
- Providers
- Documentation

Status

100%

---

## Phase 1 — Core Runtime

Completed

- Provider Layer
- Pipeline
- Conversation
- Workspace
- Tool Registry
- Tool Manager
- Agent Executor
- Execution Engine
- Planner Abstraction
- ReAct Planner
- Reflection Planner
- Agent Trace
- Execution Context

Status

100%

---

## Phase 2 — Advanced Planning

Purpose

Separate reasoning strategy from execution mechanics.

Planned

- Planner Registry
- Planner Factory
- Tree of Thought
- Debate Planner
- Self Consistency
- Multi-Agent Planner
- Hierarchical Planning
- Memory Aware Planning

Status

Beginning

---

## Phase 3 — Native Desktop

Purpose

Hermes becomes a native desktop application.

Planned

- Native Window
- Workspace Explorer
- Agent Dashboard
- Live Trace Viewer
- Background Tasks
- Visual Planning Graph
- Glassmorphism UI
- Live Animated Background
- Integrated Terminal

Status

Not Started

---

## Phase 4 — Hermes IDE

Purpose

Hermes becomes an autonomous development environment.

Planned

- File Explorer
- Editor
- Git Integration
- Autonomous Coding
- Test Runner
- Build Runner
- Debug Runner
- Reflection Viewer
- Workspace Intelligence

---

## Phase 5 — Desktop Runtime

Purpose

Hermes evolves into an AI operating layer.

Planned

- Notification Center
- Plugin SDK
- Process Manager
- Resource Monitor
- Memory Viewer
- Background Agents
- Task Scheduler

---

## Phase 6 — Retro Edition

Purpose

Alternative UI.

Same engine.

Different presentation.

Planned

- ASCII Interface
- ANSI Graphics
- CRT Theme
- Keyboard First
- Retro Terminal
- Matrix Theme

---

## Phase 7 — Distributed Intelligence

Planned

- Cloud Agents
- Remote Executors
- Distributed Planning
- Shared Memory
- Multi-Machine Runtime

---

# 5. Current Position

Current Sprint

Sprint 8

Execution Context

Cancellation

Current Progress

Core Runtime

██████████████████████████████

Advanced Planning

██░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Desktop

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Retro UI

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

---

# 6. Current Project State

Current test status

409 tests passing

0 failures

Current Python Version

Python 3.12.x

Execution subsystem

Production Ready

---

# 7. Frozen Architecture

The following interfaces are considered stable.

Changing them requires architectural justification.

PipelineProtocol

Status

FROZEN

ConversationState

Status

FROZEN

ToolRunner

Status

FROZEN

ExecutionEngine

Status

FROZEN

Planner Protocol

Status

FROZEN

Workspace

Stable

Tool Manager

Stable

Trace System

Stable

Execution Context

Stable

---

# 8. Architecture

High Level

User

↓

AgentExecutor

↓

Planner

↓

ExecutionEngine

↓

Pipeline

↓

LLM Provider

↓

ToolRunner

↓

Workspace

Planner decides

ExecutionEngine executes

Trace observes

ConversationState stores history

No component should own more than one responsibility.

---

# 9. Development Workflow

Every feature follows:

1.

Architecture Proposal

↓

2.

Architectural Review

↓

3.

Approval

↓

4.

Implementation

↓

5.

Testing

↓

6.

Freeze

Never skip architectural review.

---

# 10. Coding Rules

Always

✔ Full files

✔ Production quality

✔ SOLID

✔ Type hints

✔ Explicit interfaces

✔ Small focused classes

✔ Minimal coupling

Never

❌ Patches

❌ Massive redesigns

❌ Hidden globals

❌ Tight coupling

❌ Breaking frozen APIs

❌ Magic implementations

---

# 11. AI Rules

Every AI continuing Hermes must:

Read this document first.

Inspect the current repository.

Determine the current sprint.

Understand frozen interfaces.

Continue incrementally.

If architecture is uncertain

STOP

Produce proposal

Wait for approval.

Never redesign unrelated systems.

Never replace stable abstractions because "simpler."

---

# 12. Current Technical Debt

Known future work

Planner Registry

Planner Factory

Cancellation propagation

Streaming planner

Cost budgeting

Memory system

Desktop frontend

Native terminal

Plugin SDK

Distributed runtime

These are intentional future milestones.

Do not "fix" them by redesigning the architecture.

---

# 13. Native UI Vision

Hermes will become a native desktop application.

Modern Edition

- Glassmorphism
- Live GPU Background
- Animated gradients
- Workspace Explorer
- Terminal
- Trace Timeline
- Agent Dashboard
- Goal Tree
- Task Graph
- Resource Usage

Execution must be completely transparent.

The user should always know:

- what Hermes is doing
- why
- which tool
- which file
- which planner
- current goal
- current progress

---

# 14. Native Terminal Vision

Hermes will eventually own its own terminal.

Hermes will NOT rely on Windows Terminal.

The integrated terminal becomes part of Hermes Desktop.

The AI itself executes commands through Hermes Terminal.

Features

- PTY backend
- Command history
- Live execution
- Background jobs
- File previews
- Progress rendering
- Reflection status

---

# 15. Retro Edition Vision

The Retro Edition is NOT a separate engine.

It is a different presentation layer.

Same runtime.

Same planners.

Same execution engine.

Different UI.

Features

- ASCII
- ANSI
- CRT
- Matrix aesthetics
- Keyboard first
- Minimal interface

---

# 16. Future Autonomous Capabilities

Hermes will eventually:

Create files

Modify files

Run builds

Execute tests

Read logs

Reflect on failures

Retry automatically

Create goals

Track goals

Monitor progress

Manage workspaces

Generate plans

Manage Git

Understand projects

Maintain memory

Coordinate multiple agents

Everything must remain transparent.

The user must always be able to see what Hermes is doing.

---

# 17. Sprint History

Sprint 1

Provider abstraction

Sprint 2

Pipeline

Sprint 3

Workspace

Sprint 4

Tool system

Sprint 5

Executor

Sprint 6

Tracing

Sprint 7

Planner abstraction

Reflection

Sprint 8

Execution Context

Cancellation

Future

Planner Registry

Tree of Thought

Native Desktop

Retro UI

---

# 18. Final Principle

Hermes Genesis is intended to become an operating environment for autonomous AI rather than merely another language model wrapper.

Every architectural decision should preserve:

- modularity
- observability
- planner independence
- execution transparency
- long-term maintainability
- explicit interfaces

When uncertain:

**Extend existing abstractions.**

Do not replace them.

Architecture is more valuable than speed.