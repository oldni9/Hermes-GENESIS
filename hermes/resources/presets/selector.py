"""
===============================================================================
Hermes Runtime Preset Selector
===============================================================================
"""

from __future__ import annotations

from hermes.resources.presets.preset import RuntimePreset


class RuntimePresetSelector:

    def select(
        self,
        presets: list[RuntimePreset],
    ) -> RuntimePreset | None:

        if not presets:

            return None

        return presets[0]
