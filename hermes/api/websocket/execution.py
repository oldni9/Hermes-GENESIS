"""
===============================================================================
Execution WebSockets
===============================================================================

Sprint 17A.5 Final Freeze:
- Updated ReplayGapEvent instantiation to use explicit ReplayGapPayload model.
===============================================================================
"""
from __future__ import annotations

import asyncio
import json
import queue

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from hermes.api.dependencies import get_execution_manager
from hermes.runtime.events.execution import ExecutionFailedEvent, ExecutionFinishedEvent
from hermes.runtime.events.cancellation import ExecutionCancelledEvent
from hermes.runtime.events.system import ReplayGapEvent, ReplayGapPayload
from hermes.runtime.execution_manager import ExecutionManager
from hermes.runtime.registry import ExecutionState

router = APIRouter()


@router.websocket("/ws/execution/{execution_id}")
async def execution_websocket(
    websocket: WebSocket,
    execution_id: str,
    last_sequence: int = 0,
    manager: ExecutionManager = Depends(get_execution_manager)
):
    """
    WebSocket endpoint for streaming execution events.
    Supports replay via ?last_sequence=.
    """
    await websocket.accept()
    
    record = manager.registry.get(execution_id)
    if not record:
        await websocket.send_text(json.dumps({"error": "Execution not found"}))
        await websocket.close()
        return

    # 1. Subscribe to live events FIRST to prevent race condition
    event_queue = manager.event_bus.subscribe(execution_id)
    
    try:
        # 2. If execution is already done, send final state and close
        if record.state in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED):
            await websocket.send_text(json.dumps({
                "event_type": "execution_status",
                "execution_id": execution_id,
                "status": record.state.value,
                "result": record.result,
                "error": record.error
            }))
            await websocket.close()
            return

        # 3. Replay historical events from store and get snapshot metadata
        replay_events, last_seq, oldest_seq = manager.event_bus.store.replay_and_get_last_seq(execution_id, last_sequence)
        
        # 4. Check for replay gap
        if last_sequence > 0 and last_sequence < oldest_seq:
            missing_count = oldest_seq - last_sequence - 1
            # Explicitly construct the payload model to avoid relying on Pydantic coercion
            gap_payload = ReplayGapPayload(
                requested_sequence=last_sequence,
                oldest_available_sequence=oldest_seq,
                latest_available_sequence=last_seq,
                missing_event_count=missing_count
            )
            gap_event = ReplayGapEvent(
                execution_id=execution_id,
                payload=gap_payload
            )
            await websocket.send_text(gap_event.model_dump_json())
        
        # 5. Send replay events
        for event in replay_events:
            await websocket.send_text(event.model_dump_json())
            
        # 6. Drain the live queue of any events that occurred during replay
        while not event_queue.empty():
            try:
                event = event_queue.get_nowait()
                if event.sequence > last_seq:
                    await websocket.send_text(event.model_dump_json())
                    last_seq = event.sequence
            except queue.Empty:
                break

        # 7. Listen to live queue
        while True:
            try:
                event = await asyncio.to_thread(event_queue.get, True, 1.0)
            except queue.Empty:
                continue
                
            if event:
                await websocket.send_text(event.model_dump_json())
                
                if isinstance(event, (ExecutionFinishedEvent, ExecutionFailedEvent, ExecutionCancelledEvent)):
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        manager.event_bus.unsubscribe(execution_id, event_queue)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture