"""
===============================================================================
Hermes Runtime Resource Manager

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from hermes.resources.loader import RuntimeResourceLoader
from hermes.resources.registry import RuntimeResourceRegistry
from hermes.resources.resource import RuntimeResource
from hermes.resources.validator import RuntimeResourceValidator


class RuntimeResourceManager:
    """
    Loads and registers all runtime resources.
    """

    def __init__(self) -> None:

        self.loader = RuntimeResourceLoader()

        self.validator = RuntimeResourceValidator()

        self.registry = RuntimeResourceRegistry()

    # ------------------------------------------------------------------

    def load_directory(
        self,
        directory: Path,
    ) -> None:

        for resource_data in self.loader.load(directory):

            self.validator.validate(resource_data)

            resource = RuntimeResource(
                name=resource_data["name"],
                enabled=resource_data.get(
                    "enabled",
                    True,
                ),
                metadata=resource_data.get(
                    "metadata",
                    {},
                ),
            )

            self.registry.register(resource)

    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimeResource | None:

        return self.registry.get(name)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeResource]:

        return self.registry.all()