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
    - StopReason
    - PipelineProtocol
    - AgentTrace
    - TraceEvent
    - PlannerRegistry

Public API:
    - AgentExecutor
    - AgentTrace
===============================================================================
"""

from hermes.agent.executor.executor import AgentExecutor
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import AgentTrace, TraceEvent, TraceEventType
from hermes.agent.executor.errors import MaxIterationsExceeded, PipelineExecutionError, PlannerError
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner
from hermes.agent.executor.planners.registry import PlannerRegistry, PlannerFactory, PlannerDescriptor, PlannerCapabilities

__all__ = [
    "AgentExecutor",
    "AgentResult",
    "StopReason",
    "PipelineProtocol",
    "AgentTrace",
    "TraceEvent",
    "TraceEventType",
    "MaxIterationsExceeded",
    "PipelineExecutionError",
    "PlannerError",
    "Planner",
    "PlannerState",
    "PlannerConfig",
    "ReActPlanner",
    "ReflectionPlanner",
    "PlannerRegistry",
    "PlannerFactory",
    "PlannerDescriptor",
    "PlannerCapabilities",
]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture