"""
===============================================================================
Hermes Provider Client
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class BaseProviderClient(ABC):
    """
    Base interface for every provider implementation.
    """

    @abstractmethod
    def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        ...