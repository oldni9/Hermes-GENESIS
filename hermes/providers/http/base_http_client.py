"""
===============================================================================
Hermes Base HTTP Client
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class BaseHTTPClient(ABC):

    base_url: str = ""

    @abstractmethod
    def execute(
        self,
        request: ProviderRequest,
    ) -> ProviderResult: ...
