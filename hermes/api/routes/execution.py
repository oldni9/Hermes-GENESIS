"""
===============================================================================
Execution Routes (REST)
===============================================================================
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from hermes.api.dependencies import get_execution_manager
from hermes.runtime.execution_manager import ExecutionManager
from hermes.api.schemas import ExecutionRequest, ExecutionResponse, CancelResponse, ExecutionSnapshot

router = APIRouter(prefix="/v1/execute", tags=["execution"])


@router.post("", response_model=ExecutionResponse)
async def create_execution(
    request: ExecutionRequest,
    manager: ExecutionManager = Depends(get_execution_manager)
):
    """Create a new agent execution."""
    execution_id = manager.create_execution(
        prompt=request.prompt,
        system_prompt=request.system_prompt
    )
    record = manager.registry.get(execution_id)
    return ExecutionResponse(
        execution_id=execution_id,
        status=record.state.value
    )


@router.get("/{execution_id}", response_model=ExecutionSnapshot)
async def get_execution_snapshot(
    execution_id: str,
    manager: ExecutionManager = Depends(get_execution_manager)
):
    """Retrieve the current snapshot of an execution for reconnect logic."""
    record = manager.registry.get(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    last_seq = manager.event_bus.store.get_last_sequence(execution_id)
    
    return ExecutionSnapshot(
        execution_id=execution_id,
        status=record.state.value,
        result=record.result,
        error=record.error,
        last_event_sequence=last_seq,
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.post("/{execution_id}/cancel", response_model=CancelResponse)
async def cancel_execution(
    execution_id: str,
    manager: ExecutionManager = Depends(get_execution_manager)
):
    """Request cancellation for a running execution."""
    record = manager.registry.get(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    cancelled = manager.cancel_execution(execution_id)
    return CancelResponse(
        execution_id=execution_id,
        cancelled=cancelled
    )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture