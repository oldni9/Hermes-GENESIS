"""
===============================================================================
Hermes Runtime Session

Represents one running Hermes runtime session.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class RuntimeSession:
    """
    Runtime session.

    A new session is created every time Hermes starts.
    """

    session_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    provider: str = ""

    model: str = ""

    workspace: str = ""

    metadata: dict = field(
        default_factory=dict,
    )
