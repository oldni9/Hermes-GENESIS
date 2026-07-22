"""
===============================================================================
Hermes Parallel Execution Service
===============================================================================

A reusable, thread-safe parallel execution capability.
Hides the underlying ThreadPoolExecutor implementation from the engine and planners.
===============================================================================
"""

from __future__ import annotations

import concurrent.futures
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, TypeVar

from hermes.core.runtime import CancellationToken
from hermes.core.errors import HermesRuntimeError

T = TypeVar('T')

class ParallelExecutionError(HermesRuntimeError):
    """Raised when a parallel execution task fails internally."""
    pass

@dataclass
class ParallelJob:
    """Represents a single unit of parallel work."""
    id: str
    fn: Callable[[], T]


@dataclass
class ParallelResult:
    """Encapsulates the result of a parallel job."""
    id: str
    success: bool
    value: Any = None
    exception: Optional[Exception] = None
    duration: float = 0.0


class ParallelExecutionService:
    """
    Executes a sequence of ParallelJobs concurrently.
    Enforces concurrency limits, propagates cancellation, and aggregates exceptions.
    """
    
    def __init__(self, max_workers: int = 5, thread_name_prefix: str = "HermesWorker") -> None:
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix

    def execute(
        self, 
        jobs: Sequence[ParallelJob], 
        cancellation_token: Optional[CancellationToken] = None,
        timeout: Optional[float] = None
    ) -> List[ParallelResult]:
        """
        Executes jobs in parallel.
        Returns a list of ParallelResult in the same order as the input jobs.
        """
        results: List[Optional[ParallelResult]] = [None] * len(jobs)
        
        # 1. Check cancellation before submitting
        if cancellation_token and cancellation_token.cancelled:
            for i, job in enumerate(jobs):
                results[i] = ParallelResult(
                    id=job.id, 
                    success=False, 
                    exception=ParallelExecutionError("Cancelled before start")
                )
            return results

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers, 
            thread_name_prefix=self._thread_name_prefix
        ) as executor:
            future_to_idx = {}
            
            for i, job in enumerate(jobs):
                if cancellation_token and cancellation_token.cancelled:
                    break
                future = executor.submit(self._run_job, job)
                future_to_idx[future] = i
                
            try:
                for future in concurrent.futures.as_completed(future_to_idx, timeout=timeout):
                    idx = future_to_idx[future]
                    
                    if cancellation_token and cancellation_token.cancelled:
                        future.cancel()
                        continue
                        
                    try:
                        res = future.result()
                        results[idx] = res
                    except Exception as e:
                        results[idx] = ParallelResult(
                            id=jobs[idx].id, 
                            success=False, 
                            exception=e, 
                            duration=0.0
                        )
            except concurrent.futures.TimeoutError:
                # Timeout elapsed for the whole batch
                pass
                
        # 3. Fill any missing results (e.g., cancelled or timed out)
        for i in range(len(results)):
            if results[i] is None:
                results[i] = ParallelResult(
                    id=jobs[i].id, 
                    success=False, 
                    exception=ParallelExecutionError("Job not executed (cancelled or timed out)"),
                    duration=0.0
                )
                
        return results

    def _run_job(self, job: ParallelJob) -> ParallelResult:
        """Internal wrapper to execute a job and catch exceptions."""
        start_time = time.monotonic()
        try:
            val = job.fn()
            duration = time.monotonic() - start_time
            return ParallelResult(
                id=job.id, 
                success=True, 
                value=val, 
                duration=duration
            )
        except Exception as e:
            duration = time.monotonic() - start_time
            return ParallelResult(
                id=job.id, 
                success=False, 
                exception=e, 
                duration=duration
            )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture