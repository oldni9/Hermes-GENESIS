"""
===============================================================================
Hermes Model
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any

from hermes.capability.enums import CapabilityType
from hermes.providers.enums import ProviderType
from hermes.models.enums import ModelType


@dataclass(slots=True)
class Model:

    name: ModelType

    provider: ProviderType

    capabilities: set[CapabilityType]

    priority: int = 100

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)