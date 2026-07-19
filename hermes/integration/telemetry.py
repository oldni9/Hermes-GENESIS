"""
===============================================================================
Hermes Integration Telemetry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IntegrationTelemetry:

    executions: int = 0

    successful: int = 0

    failed: int = 0
