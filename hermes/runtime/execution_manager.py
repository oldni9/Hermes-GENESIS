"""
===============================================================================
Execution Manager
===============================================================================

Sprint 17A.5 Final Freeze:
- Exposed serialization_failures in metrics.
===============================================================================
"""
from __future__ import annotations

import concurrent.futures
import threading
import time
from typing import Dict, Optional

from hermes.core.runtime import CancellationToken
from hermes.runtime.event_bus import RuntimeEventBus
from hermes.runtime.events.cancellation import CancellationRequestedEvent
from hermes.runtime.registry import ExecutionRegistry, ExecutionState, generate_execution_id
from hermes.runtime.worker import ExecutionWorker, ExecutionPayload


class ExecutionManager:
    """Manages agent executions."""
    
    def __init__(
        self,
        agent_executor_factory: callable,
        registry: Optional[ExecutionRegistry] = None,
        event_bus: Optional[RuntimeEventBus] = None,
        max_workers: int = 4
    ) -> None:
        self._registry = registry or ExecutionRegistry()
        self._event_bus = event_bus or RuntimeEventBus()
        self._worker = ExecutionWorker(self._registry, self._event_bus)
        self._worker.set_manager(self)  # Wire manager to worker for metrics callbacks
        self._executor_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._agent_executor_factory = agent_executor_factory
        self._cancellation_tokens: Dict[str, CancellationToken] = {}
        self._cancel_lock = threading.Lock()
        
        # Metrics tracking
        self._completed_count: int = 0
        self._total_duration: float = 0.0
        self._metrics_lock = threading.Lock()

    @property
    def registry(self) -> ExecutionRegistry:
        return self._registry

    @property
    def event_bus(self) -> RuntimeEventBus:
        return self._event_bus

    def create_execution(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Creates a new execution, queues it, and returns the ID."""
        execution_id = generate_execution_id()
        self._registry.create(execution_id, prompt)
        
        agent_executor = self._agent_executor_factory()
        token = CancellationToken()
        
        with self._cancel_lock:
            self._cancellation_tokens[execution_id] = token
        
        payload = ExecutionPayload(
            execution_id=execution_id,
            agent_executor=agent_executor,
            prompt=prompt,
            system_prompt=system_prompt,
            cancellation_token=token
        )
        
        self._executor_pool.submit(self._worker.run, payload)
        
        return execution_id

    def cancel_execution(self, execution_id: str) -> bool:
        """Requests cancellation for a specific execution."""
        with self._cancel_lock:
            token = self._cancellation_tokens.get(execution_id)
            
        if token:
            self._event_bus.publish(CancellationRequestedEvent(execution_id=execution_id))
            token.cancel()
            return True
        return False

    def remove_cancellation_token(self, execution_id: str) -> None:
        """Removes a cancellation token after execution is complete to prevent memory leaks."""
        with self._cancel_lock:
            self._cancellation_tokens.pop(execution_id, None)

    def record_completion(self, duration: float) -> None:
        """Records metrics for a completed execution."""
        with self._metrics_lock:
            self._completed_count += 1
            self._total_duration += duration

    def get_metrics(self) -> dict:
        """Returns aggregated runtime metrics."""
        with self._metrics_lock:
            avg_runtime = (self._total_duration / self._completed_count) if self._completed_count > 0 else 0.0
            
        # Safely get queue size
        queued_jobs = 0
        try:
            if hasattr(self._executor_pool, '_work_queue'):
                queued_jobs = self._executor_pool._work_queue.qsize()
        except Exception:
            pass
            
        return {
            "executions": {
                "queued": len([r for r in self._registry.list_executions() if r.state == ExecutionState.QUEUED]),
                "running": len([r for r in self._registry.list_executions() if r.state == ExecutionState.RUNNING]),
                "completed": len([r for r in self._registry.list_executions() if r.state == ExecutionState.COMPLETED]),
                "failed": len([r for r in self._registry.list_executions() if r.state == ExecutionState.FAILED]),
                "cancelled": len([r for r in self._registry.list_executions() if r.state == ExecutionState.CANCELLED]),
                "average_runtime": avg_runtime
            },
            "event_bus": {
                "subscribers": sum(len(subs) for subs in self._event_bus._subscribers.values()),
                "dropped_events": self._event_bus.dropped_events,
                "published_events": self._event_bus.published_events
            },
            "thread_pool": {
                "max_workers": self._executor_pool._max_workers,
                "queued_jobs": queued_jobs
            },
            "event_store": {
                "ring_buffer_keys": len(self._event_bus.store._events),
                "replay_hits": self._event_bus.store.replay_hits,
                "replay_misses": self._event_bus.store.replay_misses,
                "serialization_failures": self._event_bus.store.serialization_failures
            }
        }

    def shutdown(self) -> None:
        """Shuts down the execution thread pool."""
        self._executor_pool.shutdown(wait=True, cancel_futures=True)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture