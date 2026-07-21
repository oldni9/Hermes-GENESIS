"""
===============================================================================
Agent Executor Package
===============================================================================

Dependencies:
    - hermes.agent.executor.executor
    - hermes.agent.executor.protocols
    - hermes.agent.executor.result
    - hermes.agent.executor.trace

Consumes:
    - None directly (re-exports)

Produces:
    - AgentExecutor
    - AgentResult
    - PipelineProtocol
    - AgentTrace
    - TraceEvent

Public API:
    - AgentExecutor
    - AgentTrace

Future Extensibility:
    The executor package intentionally isolates planning from execution. 
    Future planners (Tree-of-Thought, Reflection, Multi-Agent, Self-Critique, 
    Planner/Executor separation) can replace `ReActLoop` without changing 
    `AgentExecutor`, `ToolRunner`, or `ConversationState`.
===============================================================================
"""

from hermes.agent.executor.executor import AgentExecutor
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult
from hermes.agent.executor.trace import AgentTrace, TraceEvent, TraceEventType
from hermes.agent.executor.errors import MaxIterationsExceeded, PipelineExecutionError
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner

__all__ = [
    "AgentExecutor",
    "AgentResult",
    "PipelineProtocol",
    "AgentTrace",
    "TraceEvent",
    "TraceEventType",
    "MaxIterationsExceeded",
    "PipelineExecutionError",
    "Planner",
    "PlannerState",
    "PlannerConfig",
    "ReActPlanner",
    "ReflectionPlanner",
]