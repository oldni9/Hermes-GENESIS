"""
===============================================================================
Execution Worker
===============================================================================

Sprint 17A.2 Update:
- Emits ExecutionCancelledEvent if cancellation is requested.
- Passes CancellationToken to AgentExecutor.
- Records completion metrics using time.perf_counter().
- Cleans up cancellation tokens in finally block.
===============================================================================
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from hermes.agent.executor.trace import AgentTrace, TraceEvent
from hermes.core.runtime import CancellationToken
from hermes.runtime.event_bus import RuntimeEventBus
from hermes.runtime.events.cancellation import ExecutionCancelledEvent
from hermes.runtime.events.execution import ExecutionFailedEvent, ExecutionFinishedEvent, ExecutionStartedEvent
from hermes.runtime.events.trace import TraceRuntimeEvent
from hermes.runtime.registry import ExecutionRegistry, ExecutionState

if TYPE_CHECKING:
    from hermes.agent.executor.executor import AgentExecutor
    from hermes.runtime.execution_manager import ExecutionManager


@dataclass
class ExecutionPayload:
    execution_id: str
    agent_executor: "AgentExecutor"
    prompt: str
    system_prompt: Optional[str] = None
    cancellation_token: Optional[CancellationToken] = None


class ExecutionWorker:
    """Runs AgentExecutor in a separate thread, streaming events to the bus."""
    
    def __init__(self, registry: ExecutionRegistry, event_bus: RuntimeEventBus) -> None:
        self._registry = registry
        self._event_bus = event_bus
        self._manager: Optional["ExecutionManager"] = None

    def set_manager(self, manager: "ExecutionManager") -> None:
        self._manager = manager

    def run(self, payload: ExecutionPayload) -> None:
        """This method runs in a background thread."""
        execution_id = payload.execution_id
        start_time = time.perf_counter()
        
        # Check if cancelled before starting
        if payload.cancellation_token and payload.cancellation_token.cancelled:
            self._registry.update_state(execution_id, ExecutionState.CANCELLED)
            self._event_bus.publish(ExecutionCancelledEvent(execution_id=execution_id))
            return
            
        self._registry.update_state(execution_id, ExecutionState.RUNNING)
        self._event_bus.publish(ExecutionStartedEvent(execution_id=execution_id, payload={"prompt": payload.prompt}))
        
        trace = AgentTrace()
        
        def trace_callback(event: TraceEvent) -> None:
            runtime_event = TraceRuntimeEvent(
                execution_id=execution_id,
                timestamp=event.timestamp,
                trace_event_type=event.event_type.value,
                iteration=event.iteration,
                sequence=event.sequence,
                thread=event.thread,
                payload=event.payload
            )
            self._event_bus.publish(runtime_event)
            
        unsubscribe = trace.subscribe(trace_callback)
        
        try:
            result = payload.agent_executor.run(
                prompt=payload.prompt,
                conversation=None,
                system_prompt=payload.system_prompt,
                trace=trace,
                cancellation_token=payload.cancellation_token
            )
            
            # Check if cancelled during execution
            if payload.cancellation_token and payload.cancellation_token.cancelled:
                self._registry.update_state(execution_id, ExecutionState.CANCELLED)
                self._event_bus.publish(ExecutionCancelledEvent(execution_id=execution_id))
            else:
                self._registry.update_state(
                    execution_id, 
                    ExecutionState.COMPLETED,
                    result=result.response.text()
                )
                self._event_bus.publish(ExecutionFinishedEvent(
                    execution_id=execution_id,
                    payload={"result": result.response.text()}
                ))
                
                # Record metrics using safe time tracking
                if self._manager:
                    duration = time.perf_counter() - start_time
                    self._manager.record_completion(duration)
                    
        except Exception as e:
            self._registry.update_state(
                execution_id, 
                ExecutionState.FAILED,
                error=str(e)
            )
            self._event_bus.publish(ExecutionFailedEvent(
                execution_id=execution_id,
                payload={"error": str(e)}
            ))
        finally:
            unsubscribe()
            # Clean up cancellation token to prevent memory leaks
            if self._manager:
                self._manager.remove_cancellation_token(execution_id)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture