"""
===============================================================================
Hermes Runtime Policy Profile

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePolicyProfile:
    """
    Policy profile.

    Allows switching between multiple policy sets.
    """

    name: str

    policy: str

    enabled: bool = True
