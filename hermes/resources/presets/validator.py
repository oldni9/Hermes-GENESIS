"""
===============================================================================
Hermes Runtime Preset Validator
===============================================================================
"""

from __future__ import annotations

from hermes.resources.presets.preset import RuntimePreset


class RuntimePresetValidator:

    def validate(
        self,
        preset: RuntimePreset,
    ) -> None:

        if not preset.name.strip():

            raise ValueError("Preset name cannot be empty.")
