# HERMES GENESIS
## Master Context
Version: Sprint 8 Preparation

===========================================================================
PROJECT PHILOSOPHY
===========================================================================

Hermes is NOT a chatbot.

Hermes is a local AI Operating System.

Long-term vision:

Windows
│
├── Files
├── Processes
├── Applications
├── Browser
├── Projects
├── Git
├── Python
├── Docker
├── Internet
└── Hermes

Eventually Hermes becomes another "user" on the machine.

It can:

• inspect projects
• execute code
• fix failures
• manage repositories
• write software
• create goals
• remember work
• plan work
• monitor background jobs
• interact through a custom terminal
• interact through a desktop GUI

Hermes should eventually feel closer to Jarvis or Devin than ChatGPT.

===========================================================================
CORE DESIGN PRINCIPLES
===========================================================================

Everything is modular.

NO God objects.

NO giant files.

Protocols over inheritance.

Composition over coupling.

Every subsystem should be replaceable.

Examples:

Provider
Pipeline
Planner
ExecutionEngine
Workspace
ToolRunner
ConversationState

All replaceable.

Nothing should know implementation details.

===========================================================================
CODING RULES
===========================================================================

Strict typing.

Python 3.12+

No redesign unless requested.

Never "improve architecture" unless explicitly asked.

Preserve existing public APIs.

Every PR should be additive whenever possible.

Large rewrites only if architecturally necessary.

Always prefer:

new module

instead of

modifying existing stable module.

===========================================================================
WORKFLOW
===========================================================================

We NEVER generate patches.

We ALWAYS rewrite complete files.

If a file changes:

rewrite entire file.

If file is large:

split into chunks.

Every completed file ends with:

VERIFICATION

✔ imports
✔ typing
✔ compatibility
✔ syntax
✔ architecture

===========================================================================
CURRENT TEST STATUS
===========================================================================

Current state:

409 tests passing

0 failures

Only warnings:

Deprecated Chat(manager=...)

No functional failures.

Execution subsystem is considered stable.

===========================================================================
PROJECT EVOLUTION
===========================================================================

Sprint 1

Configuration

Logging

Bootstrap

Startup

Providers

===========================================================================
Sprint 2

Pipeline

Router

Manager

Provider registry

Model registry

Caching

===========================================================================
Sprint 3

Workspace

Namespaces

Tool Manager

Tool Registry

Tool Context

Workspace isolation

===========================================================================
Sprint 4

Conversation

Serializer

Request Builder

Context Factory

Tool Runner

===========================================================================
Sprint 5

Agent Executor

ReAct Loop

Conversation State

Execution

Tool orchestration

===========================================================================
Sprint 6

Observability

AgentTrace

TraceEvent

Metrics

Timing

Token accounting

Structured traces

===========================================================================
Sprint 7

Planner abstraction

Execution Engine

Planner protocol

Reflection Planner

ReAct Planner

Planner independence

Execution mechanics separated from planning strategy

===========================================================================
CURRENT EXECUTION ARCHITECTURE
===========================================================================

AgentExecutor

↓

Planner

↓

ExecutionEngine

↓

Pipeline

↓

Provider

Planner never executes tools.

ExecutionEngine never decides strategy.

Perfect separation.

===========================================================================
EXECUTION ENGINE RESPONSIBILITIES
===========================================================================

ExecutionEngine owns:

LLM calls

Tool execution

Conversation sequencing

OpenAI tool ordering

Retry mechanics

Tool loop

ExecutionEngine DOES NOT own:

Planning

Reflection

Tree search

Debate

Scoring

Those belong to planners.

===========================================================================
PLANNER RESPONSIBILITIES
===========================================================================

Planner decides:

continue

finish

abort

reflect

branch

debate

search

The planner owns reasoning.

The engine owns mechanics.

This separation is now frozen.

===========================================================================
CURRENT TRACE SYSTEM
===========================================================================

AgentTrace records:

LLM start

LLM finish

Tool start

Tool finish

Execution start

Execution finish

Planner events

Reflection events

Completion

Failures

Metrics

Token usage

Duration

Every planner shares same trace object.

Future planners simply emit new event types.

===========================================================================
EXECUTION IS FROZEN
===========================================================================

Execution subsystem should now remain stable.

Future work should build ON TOP.

Not rewrite.

Everything after Sprint 7 assumes:

ExecutionEngine

Planner

Trace

Conversation

Tool Runner

are stable APIs.

# HERMES GENESIS
## MASTER CONTEXT
### PART 2 — LONG TERM ROADMAP & VISION

===============================================================================
THE ULTIMATE GOAL
===============================================================================

Hermes is not being built to become another LLM wrapper.

Hermes is being built as a complete AI Operating Environment.

Eventually Hermes should feel like a second developer sitting beside the user.

The user should no longer think:

"I am using ChatGPT."

Instead they should feel:

"I am working together with Hermes."

Hermes should eventually become capable of:

• Planning work
• Executing work
• Verifying work
• Reflecting
• Learning
• Managing projects
• Using tools
• Using the terminal
• Running software
• Inspecting repositories
• Understanding failures
• Recovering automatically
• Working for hours safely

===============================================================================
LONG TERM ARCHITECTURE
===============================================================================

                    Desktop UI
                         │
        ┌────────────────┴────────────────┐
        │                                 │
    Activity Feed                   Workspace View
        │                                 │
        └──────────────┬──────────────────┘
                       │
                 Hermes Runtime
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     Planner      Execution      Memory
        │           Engine          │
        └──────┬──────────────┬─────┘
               │              │
          Pipeline        Tool System
               │
          Providers

Everything below the UI should be reusable.

The frontend should never know implementation details.

===============================================================================
PROJECT PHASES
===============================================================================

Phase 1

Core runtime

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 2

Providers

Pipeline

Routing

Caching

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 3

Workspace

Tool system

Namespaces

Isolation

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 4

Conversation

Serialization

Context

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 5

Agent Executor

ReAct

Conversation sequencing

Tool execution

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 6

Tracing

Observability

Metrics

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 7

Planner abstraction

Reflection planner

Execution Engine

Status:
COMPLETE

-------------------------------------------------------------------------------

Phase 8

Execution Context

Cancellation

Timeouts

Budgets

Current sprint.

===============================================================================
UPCOMING PHASES
===============================================================================

SPRINT 9

Planner Registry

Planner Factory

Configuration driven planners

Goal:

No hardcoded planner selection.

Future:

planner="reflection"

planner="react"

planner="tot"

planner="debate"

should all work.

-------------------------------------------------------------------------------

SPRINT 10

Tree of Thought Planner

Generate multiple reasoning branches.

Evaluate.

Prune.

Continue.

This planner should NOT modify ExecutionEngine.

Only use it.

-------------------------------------------------------------------------------

SPRINT 11

Debate Planner

Multiple agents.

Independent reasoning.

Judge.

Consensus.

Still uses same ExecutionEngine.

-------------------------------------------------------------------------------

SPRINT 12

Memory

Conversation memory

Long-term memory

Knowledge graph

Vector storage

Reflection history

Workspace memory

-------------------------------------------------------------------------------

SPRINT 13

Native Desktop UI

First graphical interface.

Glass.

Modern.

Transparent.

Everything visible.

No fake loading.

Every animation corresponds to real work.

-------------------------------------------------------------------------------

SPRINT 14

Hermes Terminal

A completely custom terminal.

NOT cmd.exe

NOT PowerShell

NOT Windows Terminal

Hermes Terminal.

Embedded.

Agent controlled.

The AI itself performs work through this terminal.

The user can watch every command.

Every output.

Every file.

Every build.

Every failure.

Every retry.

-------------------------------------------------------------------------------

SPRINT 15

Hermes IDE

Projects

Workspace explorer

Terminal

AI

Trace

Diff viewer

Git

Everything together.

-------------------------------------------------------------------------------

SPRINT 16

ASCII Edition

Separate frontend.

Same backend.

CRT

Retro

Keyboard driven

Hackerman aesthetic.

Zero mouse required.

This is NOT replacing graphical UI.

It is another frontend.

===============================================================================
THE DESKTOP UI
===============================================================================

The graphical version should expose the AI's thoughts.

Nothing should be hidden.

Examples:

Current Goal

Current Planner

Current Iteration

Current File

Current Tool

Current Provider

Current Model

Current Cost

Current Tokens

Current Background Tasks

Current Terminal Command

Current Errors

Everything visible.

===============================================================================
BACKGROUND TASKS
===============================================================================

Hermes should eventually execute long-running work.

Examples:

Refactoring

Repository analysis

Test generation

Large code generation

Documentation

Git indexing

Project indexing

These should continue in the background.

UI should show:

Running

Waiting

Paused

Cancelled

Finished

Estimated progress

Current step

Never fake progress.

===============================================================================
AUTONOMOUS CODING
===============================================================================

Eventually Hermes should be capable of:

Create files

Delete files

Rename files

Edit files

Run tests

Run terminal

Read logs

Reflect

Retry

Run formatters

Run linters

Inspect failures

Inspect tracebacks

Search project

Understand project structure

Create TODO lists

Continue unfinished work

Recover after failures

Ask for confirmation before dangerous operations.

===============================================================================
TERMINAL PHILOSOPHY
===============================================================================

The terminal is Hermes' hands.

The GUI is Hermes' face.

The planner is Hermes' brain.

The trace is Hermes' memory.

The user should always be able to see what Hermes is typing into the terminal.

Nothing hidden.

Nothing magical.

Transparent execution.

===============================================================================
FUTURE PLUGINS
===============================================================================

Hermes should eventually support:

Git

Docker

Python

Rust

Node

VSCode

Filesystem

Browser

MCP

Databases

Cloud providers

Each plugin should expose tools.

ExecutionEngine remains unchanged.

===============================================================================
WHAT MUST NEVER HAPPEN
===============================================================================

Never redesign frozen execution APIs.

Never couple planner to provider.

Never couple planner to tools.

Never let UI depend on planner implementation.

Never duplicate execution logic.

Never duplicate tool logic.

Every future capability should compose existing modules.

Not replace them.

===============================================================================
END OF PART 2
===============================================================================


# HERMES GENESIS
## MASTER CONTEXT
### PART 3 — CURRENT ARCHITECTURE, FROZEN APIs & DEVELOPMENT STATE

===============================================================================
CURRENT PROJECT STATUS
===============================================================================

Current Project Name

Hermes Genesis

Language

Python 3.12+

Current Test Status

409 Passing

0 Failures

Only warnings:

DeprecationWarning:
Chat(manager=...)

No runtime failures.

Execution subsystem is considered production-stable.

===============================================================================
CURRENT ARCHITECTURE
===============================================================================

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

Provider

The Planner owns reasoning.

The ExecutionEngine owns execution.

Pipeline owns model invocation.

Provider owns transport.

===============================================================================
FROZEN INTERFACES
===============================================================================

The following APIs are considered frozen.

DO NOT redesign.

DO NOT merge.

DO NOT simplify.

Only extend if explicitly requested.

• AgentExecutor

• ExecutionEngine

• Planner

• PipelineProtocol

• ConversationState

• ToolRunner

• RequestBuilder

• ContextFactory

• Workspace

• ToolManager

• AgentTrace

These are the project's stable foundation.

===============================================================================
EXECUTION ENGINE
===============================================================================

ExecutionEngine is responsible for:

LLM requests

Tool execution

Conversation ordering

Tool sequencing

Retries

Looping until no tool calls remain

ExecutionEngine is NOT responsible for:

Planning

Reflection

Tree Search

Debate

Memory

Scoring

Goal management

Those belong elsewhere.

===============================================================================
PLANNERS
===============================================================================

Current planners

ReActPlanner

ReflectionPlanner

Planner interface is intentionally generic.

Future planners:

TreeOfThoughtPlanner

DebatePlanner

MultiAgentPlanner

GoalPlanner

MemoryPlanner

should plug into the same interface.

ExecutionEngine should not change.

===============================================================================
TRACE SYSTEM
===============================================================================

Trace records:

Execution

Iterations

Planner events

LLM calls

Tool calls

Completion

Failure

Reflection

Timing

Token usage

Future planners should only emit new event types.

Not redesign tracing.

===============================================================================
WORKSPACE
===============================================================================

Workspace already supports

Namespaces

Isolation

Tool scoping

Filesystem context

Workspace should eventually become

Project workspace

Agent workspace

Temporary sandbox

Persistent memory workspace

===============================================================================
TOOL SYSTEM
===============================================================================

Current system

ToolRegistry

ToolManager

ToolRunner

ToolContext

Workspace

Future tools

Filesystem

Git

Docker

Browser

Python

Rust

Node

MCP

SQLite

Internet

Everything should become a tool.

===============================================================================
CURRENT DEVELOPMENT STYLE
===============================================================================

We DO NOT:

write patches

partial rewrites

TODO implementations

placeholder code

"you can implement later"

Instead:

rewrite complete files

maintain compatibility

finish implementation

verify

===============================================================================
OUR DEVELOPMENT WORKFLOW
===============================================================================

Every feature follows

Phase 1

Purpose

↓

Phase 2

Architecture

↓

Phase 3

Dependencies

↓

Phase 4

State Model

↓

Phase 5

Risks

↓

Approval

↓

Implementation

↓

Verification

No implementation starts before architecture approval.

===============================================================================
CURRENT DIRECTORY RESPONSIBILITIES
===============================================================================

bootstrap/

Startup

Providers

Dependency creation

------------------------------------------------

pipeline/

Pipeline

Routing

Caching

Execution

------------------------------------------------

providers/

Provider implementations

Groq

OpenRouter

Cerebras

Mistral

LMStudio

Ollama

------------------------------------------------

workspace/

Workspace

Namespaces

Isolation

------------------------------------------------

tools/

Registry

Manager

Runner

Context

------------------------------------------------

conversation/

Conversation models

Messages

Serialization

------------------------------------------------

agent/

Executor

Planner

Trace

Execution

Context

------------------------------------------------

memory/

(Planned)

Long-term memory

Knowledge

Embeddings

Reflection history

===============================================================================
SPRINT COMPLETION
===============================================================================

Sprint 1

Bootstrap

DONE

----------------------------

Sprint 2

Providers

DONE

----------------------------

Sprint 3

Workspace

DONE

----------------------------

Sprint 4

Conversation

DONE

----------------------------

Sprint 5

Agent Executor

DONE

----------------------------

Sprint 6

Tracing

DONE

----------------------------

Sprint 7

Planner Abstraction

Execution Engine

Reflection

DONE

----------------------------

Sprint 8

Execution Context

Cancellation

Deadline

Budget

IN PROGRESS

===============================================================================
CURRENT PRIORITY
===============================================================================

Finish Sprint 8.

Introduce

ExecutionContext

CancellationToken

Deadlines

Token budgets

Cost budgets

without breaking

ExecutionEngine

Planner

AgentExecutor

Pipeline

After Sprint 8

Planner Registry

↓

Tree Of Thought

↓

Debate Planner

↓

Memory

↓

Desktop UI

↓

Hermes Terminal

↓

ASCII Frontend

===============================================================================
UI ROADMAP
===============================================================================

Version 1

Modern desktop interface.

Glass.

Transparent.

Live execution.

Everything visible.

Examples

Current Goal

Current Planner

Current Tool

Current File

Current Command

Current Tokens

Current Cost

Current Errors

Current Background Tasks

Nothing hidden.

-------------------------------------------------------------------------------

Version 2

ASCII Edition.

Completely different frontend.

Same backend.

CRT

Retro

Minimal

Keyboard only

Hackerman aesthetic.

===============================================================================
CUSTOM TERMINAL
===============================================================================

Hermes WILL NOT permanently depend on cmd.exe.

Long term:

Hermes Terminal

will become the execution environment.

Initially

it may wrap PowerShell or cmd internally.

Eventually

Hermes Terminal becomes

its own shell

its own renderer

its own command system

its own UI.

The AI performs work inside Hermes Terminal.

The user watches.

Transparency is mandatory.

===============================================================================
IMPORTANT REMINDERS
===============================================================================

Do NOT redesign architecture.

Do NOT collapse modules.

Do NOT merge Planner into Engine.

Do NOT merge Engine into Executor.

Do NOT hide execution.

Do NOT introduce magic.

Hermes values transparency.

The user should always understand

what Hermes is doing

why it is doing it

where it is spending time

what command it executed

what file changed

what tool ran

what failed

how it recovered.

Transparency over cleverness.

Architecture over shortcuts.

Maintainability over speed.

===============================================================================
END OF MASTER CONTEXT
===============================================================================


# HERMES GENESIS
## MASTER CONTEXT
### PART 4 — DEVELOPMENT RULES, TEAMWORK & USER PREFERENCES

===============================================================================
ABOUT THE USER
===============================================================================

The user is not looking for quick prototypes.

The user is building Hermes as a serious long-term software project.

The project has been under development for months.

The user deeply values:

• architecture
• modularity
• maintainability
• transparency
• future extensibility

Do NOT treat Hermes like a weekend experiment.

===============================================================================
HOW DEVELOPMENT WORKS
===============================================================================

Every change follows this order:

1.
Discussion

↓

2.
Architecture Proposal

↓

3.
Approval

↓

4.
Implementation

↓

5.
Verification

Never skip architecture discussions.

Never jump directly into coding.

===============================================================================
FILE GENERATION RULES
===============================================================================

Always generate COMPLETE FILES.

Never generate patches.

Never say

"...existing code..."

"...rest unchanged..."

"...continue below..."

Rewrite the entire file.

If a file is too large

split it into multiple chunks.

Example

Part 1

Part 2

Part 3

until complete.

===============================================================================
WHEN MODIFYING FILES
===============================================================================

If one line changes

rewrite entire file.

This keeps version history clean.

Never output diffs.

===============================================================================
VERIFICATION
===============================================================================

Every completed file ends with

VERIFICATION

Example

VERIFICATION

✔ imports

✔ syntax

✔ typing

✔ compatibility

✔ architecture

Only then move to next file.

===============================================================================
DO NOT REDESIGN
===============================================================================

Unless the user explicitly asks

DO NOT

rename modules

move folders

merge classes

change APIs

rewrite architecture

simplify abstractions

Hermes has intentionally layered architecture.

Respect it.

===============================================================================
BACKWARD COMPATIBILITY
===============================================================================

Public APIs matter.

Avoid breaking:

imports

constructors

protocols

return values

configuration

Existing tests should continue passing.

===============================================================================
TESTS
===============================================================================

Hermes values stability.

Every change should preserve tests.

Current state

409 passing

0 failing

The goal is

never reduce that number.

===============================================================================
WHEN UNSURE
===============================================================================

Ask.

Never invent architecture.

Never guess intended behavior.

===============================================================================
CURRENT PHILOSOPHY
===============================================================================

Hermes should become

more modular

not more complicated.

Add layers only when justified.

Avoid clever code.

Prefer readable code.

===============================================================================
FUTURE FEATURES
===============================================================================

When implementing future systems

remember the final destination.

Eventually Hermes will have

Desktop UI

ASCII UI

Terminal

Memory

Planning

Reflection

Tree Search

Multi Agent

Background workers

Autonomous coding

Git

Browser

Workspace management

Every subsystem should be designed knowing these are coming.

===============================================================================
ABOUT THE UI
===============================================================================

Version 1

Modern.

Transparent.

Professional.

Everything happening live.

User sees:

Planner

Execution

Trace

Files

Commands

Terminal

Background jobs

Goals

Nothing hidden.

-------------------------------------------------------------------------------

Version 2

ASCII.

Retro.

CRT.

Minimal.

Keyboard-first.

Still powered by the exact same backend.

Frontend changes.

Backend remains identical.

===============================================================================
ABOUT THE TERMINAL
===============================================================================

Hermes will eventually use

Hermes Terminal

not Windows Terminal.

Initially

Hermes Terminal may internally execute

cmd

PowerShell

bash

etc.

Eventually

Hermes Terminal becomes

its own renderer

its own shell

its own command runtime.

The AI itself performs work there.

The user watches every command.

===============================================================================
AUTONOMOUS CODING VISION
===============================================================================

Hermes should eventually be capable of

reading repositories

understanding projects

creating files

editing files

running tests

running terminal commands

reading logs

retrying failures

reflecting

continuing interrupted work

tracking goals

tracking progress

recovering automatically

while remaining transparent.

===============================================================================
COLLABORATION STYLE
===============================================================================

The assistant is expected to behave like

a senior software architect

not merely a code generator.

Responsibilities include

identifying future risks

protecting architecture

keeping modules decoupled

maintaining consistency

thinking several sprints ahead

without losing focus on the current sprint.

===============================================================================
END GOAL
===============================================================================

When Hermes is finished

it should feel like

a complete AI operating environment

where the AI is visibly thinking,

planning,

coding,

executing,

testing,

reflecting,

and improving

while the human can observe every step.

That level of transparency is one of Hermes' defining characteristics.

===============================================================================
END OF DOCUMENT
===============================================================================
