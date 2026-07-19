"""
===============================================================================
Hermes Files Metadata
===============================================================================
"""

from __future__ import annotations

from hermes.subsystems import SubsystemCapabilities
from hermes.subsystems import SubsystemMetadata

FILES_METADATA = SubsystemMetadata(
    name="files",
    version="1.0",
    description="Hermes File Management Subsystem",
    author="Aryan",
    commands=[
        "open",
        "copy",
        "move",
        "rename",
        "delete",
        "search",
        "zip",
        "extract",
    ],
)


FILES_CAPABILITIES = SubsystemCapabilities(
    commands=FILES_METADATA.commands,
    supports_search=True,
    supports_background_tasks=True,
    supports_notifications=False,
    supports_ai_control=True,
)
