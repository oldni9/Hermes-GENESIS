"""
===============================================================================
Hermes Runtime Preset Registry
===============================================================================
"""

from __future__ import annotations

from hermes.resources.presets.preset import RuntimePreset


class RuntimePresetRegistry:

    def __init__(self) -> None:

        self._presets: dict[str, RuntimePreset] = {}

    # --------------------------------------------------------------

    def register(
        self,
        preset: RuntimePreset,
    ) -> None:

        self._presets[preset.name] = preset

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimePreset | None:

        return self._presets.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimePreset]:

        return list(self._presets.values())
