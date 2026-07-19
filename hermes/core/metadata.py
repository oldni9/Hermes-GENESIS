"""
===============================================================================
Hermes Genesis Metadata
===============================================================================

Global metadata describing the Hermes AI Operating System.

This module contains immutable project information only.
It must never depend on any other Hermes subsystem.

Author:
    Aryan + ChatGPT

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectMetadata:
    """
    Immutable metadata describing the Hermes project.
    """

    name: str
    version: str
    codename: str
    author: str
    website: str | None = None
    repository: str | None = None


HERMES = ProjectMetadata(
    name="Hermes",
    version="Genesis-0.1.0",
    codename="Genesis",
    author="Aryan",
)
