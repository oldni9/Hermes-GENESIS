"""
===============================================================================
Hermes Command Registry

Registers runtime subsystems capable of executing commands.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class CommandRegistry:
    """
    Registry of runtime subsystems.

    Examples

    - files
    - mail
    - music
    - runtime
    - terminal
    - memory
    - llm
    """

    def __init__(self) -> None:

        self._subsystems: dict[str, object] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        subsystem: object,
    ) -> None:

        self._subsystems[name.lower()] = subsystem

    # ------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:

        self._subsystems.pop(
            name.lower(),
            None,
        )

    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> object:

        return self._subsystems[name.lower()]

    # ------------------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:

        return name.lower() in self._subsystems

    # ------------------------------------------------------------------

    def names(
        self,
    ) -> list[str]:

        return sorted(
            self._subsystems.keys(),
        )

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._subsystems.clear()

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(
            self._subsystems,
        )
