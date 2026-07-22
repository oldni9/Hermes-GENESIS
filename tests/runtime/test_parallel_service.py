"""
===============================================================================
Tests for ParallelExecutionService (Sprint 12)
===============================================================================
"""
from __future__ import annotations

import time
import pytest
from hermes.runtime.parallel import ParallelExecutionService, ParallelJob, ParallelResult
from hermes.core.runtime import CancellationToken


def test_parallel_success():
    service = ParallelExecutionService(max_workers=3)
    
    def task(n):
        return n * 2
        
    jobs = [
        ParallelJob(id="1", fn=lambda: task(1)),
        ParallelJob(id="2", fn=lambda: task(2)),
        ParallelJob(id="3", fn=lambda: task(3)),
    ]
    
    results = service.execute(jobs)
    
    assert len(results) == 3
    assert all(r.success for r in results)
    
    # Verify order is preserved
    assert results[0].value == 2
    assert results[1].value == 4
    assert results[2].value == 6
    assert results[0].id == "1"

def test_parallel_exception_handling():
    service = ParallelExecutionService(max_workers=2)
    
    def failing_task():
        raise ValueError("Task failed")
        
    jobs = [
        ParallelJob(id="1", fn=lambda: "ok"),
        ParallelJob(id="2", fn=failing_task),
    ]
    
    results = service.execute(jobs)
    
    assert results[0].success is True
    assert results[0].value == "ok"
    
    assert results[1].success is False
    assert results[1].value is None
    assert isinstance(results[1].exception, ValueError)
    assert "Task failed" in str(results[1].exception)

def test_parallel_cancellation_before_start():
    service = ParallelExecutionService(max_workers=2)
    token = CancellationToken()
    token.cancel()
    
    jobs = [ParallelJob(id="1", fn=lambda: "ok")]
    results = service.execute(jobs, cancellation_token=token)
    
    assert results[0].success is False
    assert "Cancelled before start" in str(results[0].exception)

def test_parallel_preserves_order_with_variable_latency():
    service = ParallelExecutionService(max_workers=3)
    
    def slow_task():
        time.sleep(0.2)
        return "slow"
        
    def fast_task():
        time.sleep(0.01)
        return "fast"
        
    jobs = [
        ParallelJob(id="slow", fn=slow_task),
        ParallelJob(id="fast", fn=fast_task),
    ]
    
    results = service.execute(jobs)
    
    assert results[0].id == "slow"
    assert results[0].value == "slow"
    assert results[1].id == "fast"
    assert results[1].value == "fast"
    
def test_parallel_timeout_handling():
    service = ParallelExecutionService(max_workers=1)
    
    def slow_task():
        time.sleep(0.5)
        return "slow"
        
    jobs = [
        ParallelJob(id="slow", fn=slow_task),
        ParallelJob(id="fast", fn=lambda: "fast"),
    ]
    
    # Timeout should trigger before slow finishes
    results = service.execute(jobs, timeout=0.1)
    
    # At least one should fail due to timeout
    failed = [r for r in results if not r.success]
    assert len(failed) > 0
    assert "timed out" in str(failed[0].exception).lower()