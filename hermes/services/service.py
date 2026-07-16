"""
===============================================================================
Hermes Base Service

Foundation for every reusable Hermes service.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from hermes.services.context import ServiceContext
from hermes.services.metadata import ServiceMetadata
from hermes.services.result import ServiceResult


class BaseService(ABC):
    """
    Base class for every Hermes service.

    Services provide reusable capabilities that multiple
    subsystems may consume.

    Examples
    --------
    OCRService
    EmbeddingService
    SearchService
    ImageTaggingService
    TranslationService
    """

    def __init__(self) -> None:

        self.context = ServiceContext()

    # ------------------------------------------------------------

    @property
    @abstractmethod
    def metadata(self) -> ServiceMetadata:
        """
        Static metadata describing the service.
        """

    # ------------------------------------------------------------

    @property
    def name(self) -> str:

        return self.metadata.name

    # ------------------------------------------------------------

    @abstractmethod
    def startup(self) -> None:
        """
        Called when Hermes starts.
        """

    # ------------------------------------------------------------

    @abstractmethod
    def shutdown(self) -> None:
        """
        Called before Hermes exits.
        """

    # ------------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        **kwargs,
    ) -> ServiceResult:
        """
        Execute the service.
        """

    # ------------------------------------------------------------

    def __repr__(self):

        return (

            f"{self.__class__.__name__}"

            f"(name='{self.name}')"

        )