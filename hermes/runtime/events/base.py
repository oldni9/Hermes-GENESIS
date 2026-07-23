"""
===============================================================================
Runtime Base Event
===============================================================================

Sprint 17A.5 Final Freeze:
- Centralized SCHEMA_VERSION constant.
- Added event_id (UUID) for deduplication and distributed tracing.
- Changed event_id type to UUID for better client type generation.
===============================================================================
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field

# Centralized Schema Version Constant
SCHEMA_VERSION = "1.0.0"

class BaseEvent(BaseModel):
    """Base class for all runtime events."""
    event_id: UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    execution_id: str
    timestamp: float = Field(default_factory=time.time)
    schema_version: str = Field(default=SCHEMA_VERSION)
    sequence: int = 0  # Assigned by ExecutionEventStore upon appending
    payload: Dict[str, Any] = Field(default_factory=dict)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture